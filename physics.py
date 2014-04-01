#
# physics.py - classes and routines to do
# game physics
#
# Space Travel
#     Copyright (C) 2014  Eric Eveleigh
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# imports
import math
import pygame.draw
import pygame
from vector import Vector2D

class Object2D(object):
    def __init__(self, position, velocity, orientation, ang_velocity, mass):
        self.position = Vector2D(position.get_x(), position.get_y())
        self.next_position = Vector2D()
        self.velocity = Vector2D(velocity.get_x(), velocity.get_y())
        self.next_velocity = Vector2D()
        self.acceleration = Vector2D()
        self.next_acceleration = Vector2D()

        # self.orientation is direction expressed as 
        # an absolute angle from positive x in rads
        self.orientation = orientation
        self.next_orientation = 0.0
        self.ang_velocity = ang_velocity
        self.next_ang_velocity = 0.0
        self.ang_accel = 0.0
        self.next_ang_accel = 0.0

        self.last_dt = 0.0

        # tuple of position vectors of polygon points
        self.geometry = ()
        

        # bb_min
        # +-------
        # |\      |
        # | \     |
        # |  \    |
        # |   * <-- position
        # |    \  |
        # |     \ |
        # |      \|
        #  -------+
        #         bb_max
        # bounding box - *in world space*
        self.bb_min = Vector2D()
        self.bb_max = Vector2D()
        
        
        self.mass = mass
        self.force = Vector2D()

        # center of mass as vector from self.position point
        self.cm = Vector2D()
        # moment of inertia about self.orientation rotation axis
        self.moment = 0.0
        self.torque = 0.0

        # points expressed as vectors from CM
        self.phys_geom = ()
        self.phys_geom_oriented = []
        self.oriented_faces = []
        
        self.collided_with = []
        self.collidable = True
        
    def get_position(self):
        return self.position.copy()
    
    def set_position(self, position):
        self.position = position.copy()
    
    def get_velocity(self):
        return self.velocity.copy()
    
    def set_velocity(self, velocity):
        self.velocity.set_vect(velocity)
    
    def set_orientation(self, orientation):
        self.orientation = orientation
        
    def get_orientation(self):
        return self.orientation
    
    def set_ang_velocity(self, ang_velocity):
        self.ang_velocity = ang_velocity
        
    def get_ang_velocity(self):
        return self.ang_velocity
    
    def get_mass(self):
        return self.mass
    
    def set_collidable(self, collidable):
        self.collidable = collidable
        
    def get_collidable(self):
        return self.collidable
    
    def get_bounding_rect(self):
        left, top = self.bb_min.get_int()
        '''pos = self.get_position().get_int()
        left += pos[0]
        top += pos[1]
        '''
        width, height = (self.bb_max.addition(self.bb_min.reversed()).get_int()) 
        return pygame.Rect(left, top, width, height)
    # converts a point in the geometry's space
    # to a point in the world space
    def model_to_world(self, point):
        return point.rotated(self.orientation).add(self.position)
        
    # converts a point in world space to a point
    # in geometry space
    def world_to_model(self, point):
        return point.addition(self.position.reversed()).rotate_inverse(self.orientation)

    # set bounding box of self from points
    def calc_bbox(self, points):
        self.bb_min.set()
        self.bb_max.set()
        for point in points:
            if point.x < self.bb_min.x:
                self.bb_min.x = point.x
            if point.x > self.bb_max.x:
                self.bb_max.x = point.x
            if point.y < self.bb_min.y:
                self.bb_min.y = point.y
            if point.y > self.bb_max.y:
                self.bb_max.y = point.y
        self.bb_min.add(self.position)
        self.bb_max.add(self.position)
    
    # center of mass of self from points
    def calc_cm(self, points):
        # determines centroid of the set of points
        # this equals CM since uniform density is assumed
        # http://en.wikipedia.org/wiki/Center_of_mass#A_continuous_volume
        # centroid is basically 2D average of points
        cm = Vector2D()
        npoints = len(points)
        if npoints > 0:
            for point in points:
                cm.x += point.x
                cm.y += point.y
            cm.scale(1.0/npoints)
        self.cm = cm

    # calculate moment of inertia about cm
    # http://en.wikipedia.org/wiki/List_of_moments_of_inertia
    def calc_moment(self):
        points = list(self.phys_geom)
        points.append(points[0])
        n = 0
        sumtop = 0.0
        sumbottom = 0.0
        for point in self.phys_geom:
            cp = points[n]
            np = points[n+1]
            cross = np.cross2(cp)
            sumtop += cross*(np.dot(np) + np.dot(cp) + cp.dot(cp)) 
            sumbottom += cross
            n+=1
        try:
            self.moment = (self.mass * sumtop) / (60.0 * sumbottom)
        except:
            self.moment = float('+inf')
        print "Mass:",self.mass
        print "Moment:",self.moment

    # calc oriented geometry
    def get_oriented_geometry(self,orientation):
        n = 0
        phys_geom_oriented = [None]*len(self.phys_geom)
        oriented_faces = [None]*len(self.phys_geom)
        for point in self.phys_geom:
            phys_geom_oriented[n] = point.rotated(orientation)
            point1 = phys_geom_oriented[n-1]
            point2 = phys_geom_oriented[n]
            oriented_faces[n] = (point1, point2)
            n+=1
        # loop does not get first face correctly
        oriented_faces[0] = (phys_geom_oriented[-1], 
                                  phys_geom_oriented[0])
        return (phys_geom_oriented, oriented_faces)

    # re-center geometry about CM
    def calc_phys_geom(self):
        self.phys_geom = []
        for point in self.geometry:
            self.phys_geom.append(point.addition(self.cm.reversed()))
        self.phys_geom_oriented = list(self.phys_geom)
        self.oriented_faces = [(Vector2D(),Vector2D())]*len(self.phys_geom_oriented)
        #self.calc_phys_geom_oriented()
        self.phys_geom = tuple(self.phys_geom)
    
    # set geometry and calculate BB
    def set_geometry(self, points):
        self.geometry = points
        self.calc_bbox(points)
        self.calc_cm(points)
        self.calc_phys_geom()
        self.calc_moment()

    # take in force and radius and
    # add the resulting torque
    def add_torque(self, r, force):
        torque = r.cross2(force)
        self.torque += torque

    # applies the given force to given face
    def add_force(self, face, force):
        # final minus initial then get normal
        print force.norm()
        normal = face[1].addition(face[0].reversed()).normal()
        normal_force = normal.scaled(force.dot(normal)*100)
        print normal_force.norm()
        self.force.add(normal_force)
        
    def apply_force(self, force):
        self.force.add(force)
        
    def apply_oriented_force(self, magnitude):
        force = Vector2D(1, 0).rotate(self.orientation).scale(magnitude)
        self.apply_force(force)

    # Keep orientation in the range -pi < 0 <= pi.
    # Quickly rotating objects may otherwise gain very
    # large angles subject to floating point error
    def limit_orientation(self):
        # positive angles
        if self.orientation >= 0:
            # angle farther than half way
            if self.orientation > math.pi: 
                # change it to an equivalent negative angle
                self.orientation = -math.pi 
                + (self.orientation - math.pi)
        # negative angles
        else:
            if self.orientation <= -math.pi:
                self.orientation = math.pi 
                + (self.orientation + math.pi)
        
    def calc_next_state(self, dt):
        self.next_position = self.position.addition(self.velocity.scaled(dt))
        # velocity += acceleration*dt
        self.next_acceleration = (self.force.scaled(dt/self.mass))
        self.next_velocity = self.velocity.addition(self.acceleration.scaled(dt)) 
        # angular dynamics: d(-) = w*dt + 0.5 * a*dt^2
        dtheta = self.ang_velocity*dt + self.ang_accel*(0.5 * dt**2)
        self.next_orientation = self.orientation + dtheta
        #self.limit_orientation()
        
        # angular velocity += ang accel * dt
        self.next_ang_velocity = self.ang_velocity + self.ang_accel*dt 
        self.next_ang_accel = self.torque/self.moment
        
    # time step object state, dynamics, etc.
    def update(self, dt):
        self.calc_next_state(dt)
        # dynamics: dp = v*dt + 0.5 * a*dt^2
        self.position.add(self.velocity.scaled(dt))
        # velocity += acceleration*dt
        self.acceleration = (self.force.scaled(dt).scaled(1.0/self.mass))
        #self.acceleration.add(Vector2D(0,98))
        self.velocity.add(self.acceleration.scaled(dt)) 
        # angular dynamics: d(-) = w*dt + 0.5 * a*dt^2
        dtheta = self.ang_velocity*dt + self.ang_accel*(0.5 * dt**2)
        self.orientation += dtheta
        self.limit_orientation()
        #print self.orientation
        # angular velocity += ang accel * dt
        self.ang_velocity += self.ang_accel*dt 
        self.ang_accel = self.torque/self.moment

        self.torque = 0
        self.force.set(0.0,0.0)

        self.phys_geom_oriented, self.oriented_faces = self.get_oriented_geometry(self.orientation)
        
        self.last_dt = dt
        
        self.collided_with = []

    def point_abs_velocity(self, r):
        linear_vel = self.velocity
        angular_vel = self.ang_velocity
        return linear_vel.addition(r.perp().scale(angular_vel)).scaled(self.last_dt)

    def vert_abs_velocity(self, vertnum):
        vert = self.phys_geom[vertnum]
        r = vert.rotated(self.orientation)
        abs_vel = self.point_abs_velocity(r)
        linear_vel = self.velocity
        angular_vel = self.ang_velocity
        return linear_vel.addition(r.perp().scale(angular_vel))

    def vert_next_abs_velocity(self, vertnum):
        linear_vel = self.next_velocity
        angular_vel = self.next_ang_velocity
        vert = self.phys_geom[vertnum]
        r = vert.rotated(self.next_orientation)
        return linear_vel.addition(r.perp().scale(angular_vel))

    # http://en.wikipedia.org/wiki/Collision_response#Impulse-Based_Reaction_Model
    def calc_impulse(self, n, vr, r1, r2, m1, m2, I1, I2, e):
        top = vr.scaled(-(1.0 + e)).dot(n)

        bottom = (1/m1)*(n.dot(r1)**2) + (1/m2)*(n.dot(r2)**2) 

        z1 = r1.cross2(n)*(1/I1)
        z2 = r2.cross2(n)*(1/I2)
        bottom += (Vector2D.cross3(z1, r1).add(Vector2D.cross3(z2,r2))).dot(n)

        return top/bottom


    # signal that self is being hit by
    # obj and something should be done
    # about it - collision resolution
    def hit_by(self, obj, collision):
        #self.collided_with.append(obj)
        
        r1 = collision.point.addition(self.position.reversed())
        r2 = collision.point.addition(obj.position.reversed())

        r1_dir = r1.direction()
        r2_dir = r2.direction()

        v1 = self.point_abs_velocity(r1)
        v2 = obj.point_abs_velocity(r2)

        vr = v2.addition(v1.reversed())

        m1 = self.mass
        m2 = obj.mass

        I1 = self.moment
        I2 = obj.moment
        
        n = collision.normal
        jr = self.calc_impulse(n, vr, r1_dir, r2_dir, m1, m2, I1, I2, 0.5)

        v1 = v1.addition(r1_dir.scaled((jr/m1)*n.dot(r1)).reversed())
        v2 = v2.addition(r2_dir.scaled((jr/m2)*n.dot(r2)).reversed())

        w1 = self.ang_velocity
        w2 = obj.ang_velocity

        w1 = w1 - jr/I1 * r1.cross2(n)
        w2 = w2 - jr/I2 * r2.cross2(n)
        
        self.velocity = v1
        self.ang_velocity = w1

        obj.velocity = v2
        obj.ang_velocity = w2
       
    '''
    # Not needed, fixed Dynamics
    def has_collided_with(self, obj):
        for object in self.collided_with:
            if obj == object:
                return True
            
        return False
    '''
            

    # shows physics info on surface:
    # bounding box in black
    # geometry in green
    # vertice vectors in blue
    # center of mass in red
    def draw_phys(self, surface):
        # geometry, vertices, CM

        points = []
        drawpoints = []
        i = 0
        for point in self.phys_geom_oriented:
            points.append(point)
            abspoint = point.copy().add(self.position)
            drawpoints.append(abspoint.get())
            pygame.draw.line(surface, (0,0,255), 
                             self.position.get(), 
                             abspoint.get())
            velocity = self.vert_next_abs_velocity(i)
            '''
            pygame.draw.line(surface, (255,0,0),
                             abspoint.get(),
                             abspoint.addition(velocity).get())
            '''
            i += 1
            
        '''
        faces = self.get_oriented_geometry(self.orientation)[1]
        for face in faces:
            #pygame.draw.line(surface, (0,255,0), face[0].addition(self.position).get_int(), face[1].addition(self.position).get_int())
            vect = face[1].addition(face[0].reversed())
            normal = vect.normal()
            midpoint = face[0].addition(vect.scaled(0.5)).addition(self.position)
            finalpoint = midpoint.addition(normal.scaled(10))
            pygame.draw.line(surface, (255,255,0), midpoint.get_int(), finalpoint.get_int())
        '''

        # draw geom
        pygame.draw.polygon(surface, (0,255,0), drawpoints, 1)

        # calc/draw CM
        self.calc_cm(points)
        cm_abs = self.cm.addition(self.position)
        pygame.draw.circle(surface, (255,0,0), cm_abs.get_int(), 2)

        # bounding box
        '''
        self.calc_bbox(points)
        bbox = self.get_bounding_rect()
        
        pygame.draw.rect(surface, (255, 255, 255), bbox, 1)
        '''

class Collision(object):
    # obj1 is hitting obj2
    def __init__(self, obj1, obj2, point, normal, time):
        self.obj1 = obj1
        self.obj2 = obj2
        self.point = point
        self.normal = normal
        self.time = time

    def resolve(self):
        self.obj2.hit_by(self.obj1, self)
        
    def is_between(self, obj1, obj2):
        return self.obj1 == obj1 and self.obj2 == obj2

class Dynamics(object):
    def __init__(self):
        self.objects = []

    def add_object(self,obj):
        self.objects.append(obj)

    def update_all(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def update(self, dt):
        timestep = dt
        self.resolve_collisions(dt)
        self.update_all(dt)

    def rect_from_bbox(self,bbox):
        rect = pygame.Rect()
        rect.topleft = bbox[0].get_int()
        rect.bottomright = bbox[1].get_int()
        return rect

    # find if two Rects intersect
    # returns False if no intersection exists
    def bbox_intersect(self,box1, box2):
        return box1.colliderect(box2)

    def check_collisions(self, obj1, obj2, dt):
        collision = None
        geometry1 = obj1.get_oriented_geometry(obj1.next_orientation)
        geometry2 = obj2.get_oriented_geometry(obj2.next_orientation)

        # app for obj1 hitting obj2
        faces = geometry2[1]
        verts = geometry1[0]
        i = 0
        for vert in verts:
            a1 = vert.addition(obj1.position)
            a2 = a1.addition(obj1.vert_abs_velocity(i).scaled(dt))
            i += 1
            for face in faces:
                b1 = face[0].addition(obj2.next_position)
                b2 = face[1].addition(obj2.next_position)
                
                col = Vector2D.intersection(a1, a2, b1, b2)
                if col != None and (collision == None or col[1] < collision.time):
                    normal = face[1].addition(face[0].reversed()).normal() # collision normal
                    collision = Collision(obj1, obj2, col[0], normal,  col[1])
        return collision
        
    
    def find_collision(self, obj1, obj2, dt):
        '''
        returns a Collision if obj1 and obj2 will
        collide next update. Returns None if not
        '''
        # TODO: change to use next state bbox
        obj1.calc_bbox(obj1.phys_geom_oriented)
        obj2.calc_bbox(obj2.phys_geom_oriented)
        bbox1 = obj1.get_bounding_rect()
        bbox2 = obj2.get_bounding_rect()

        collision = None
        if self.bbox_intersect(bbox1, bbox2) == True:
            collision12 = self.check_collisions(obj1, obj2, dt) # obj1 on 2
            collision21 = self.check_collisions(obj2, obj1, dt) # obj2 on 1

            '''
            Check which collision happens sooner,
            or at all.
            '''
            if collision12 == None:
                collision = collision21
            elif collision21 == None:
                collision = collision12
            elif collision12.time < collision21.time:
                collision = collision12
            else:
                collision = collision21
        

        return collision
            

    def resolve_collisions(self, objects, dt):
        '''
        Iterate objects and tell them which are colliding
        Pass I:
        obj_list1 = [obj1,obj2,obj3,obj4]
        obj_list2 = [obj2,obj3,obj4]
        Pass II:
        obj_list1 = [obj1,obj2,obj3,obj4]
        obj_list2 = [obj3,obj4]
        Pass III:
        obj_list1 = [obj1,obj2,obj3,obj4]
        obj_list2 = [obj4]
        Pass IV:
        obj_list1 = [obj1,obj2,obj3,obj4]
        obj_list2 = []
        
        This function is a major bottleneck.
        The outer loop is at least O(n^2) but
        the entire function is worse.
        '''
        obj_list1 = objects
        obj_list2 = list(objects)
        for obj1 in obj_list1:
            '''
            Removing the first item in obj_list2
            each time avoids checking if objects 
            collide with themselves and also if 
            two different objects have already 
            been checked.
            '''
            obj_list2.pop(0)
            for obj2 in obj_list2:
                if obj1.get_collidable() == False:
                    continue
                if obj2.get_collidable() == False:
                    continue
                '''
                if obj1 == obj2:
                    continue
                if obj2.has_collided_with(obj1):
                    continue
                '''
                    
                obj1.calc_next_state(dt)
                obj2.calc_next_state(dt)
                collision = self.find_collision(obj1, obj2, dt)
                if collision != None:
                    collision.resolve()
