"""
main.py
-------
Entry point for the belief revision engine.
"""

from agm_tests import run_all_tests

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if "--weather" in args or "-w" in args:
        from weather import run_weather
        run_weather()
    elif "--tests" in args:
        run_all_tests()
    else:
        run_all_tests()
