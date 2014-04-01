import app
import cProfile
import pstats

DEBUG = False

if __name__=="__main__":
    if DEBUG == True:
        cProfile.run('app.main()', 'profile')
        p = pstats.Stats('profile')
        p.sort_stats('cumulative').print_stats()
    else:
        app.main()