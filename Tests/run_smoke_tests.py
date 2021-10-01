import pyjion
import re
import os
import gc
import unittest
import argparse


def main(input_file, opt_level, pgc):
    SAVEDCWD = os.getcwd()
    tests = []

    # Lifted from libregr.main
    regex = re.compile(r'\btest_[a-zA-Z0-9_]+\b')
    with open(os.path.join(SAVEDCWD, input_file)) as fp:
        for line in fp:
            line = line.split('#', 1)[0]
            line = line.strip()
            match = regex.search(line)
            if match is not None:
                tests.append(match.group())

    has_failures = False

    for test in tests:
        test_cases = unittest.defaultTestLoader.loadTestsFromName(f"test.{test}")
        print(f"Testing {test}")
        for case in test_cases:
            pyjion.enable()
            print(f"Trying with Optimizations = {opt_level}")
            pyjion.config(level=opt_level, pgc=pgc)
            r = unittest.result.TestResult()
            case.run(r)
            if r.wasSuccessful():
                print(f"All tests in case successful.")
            else:
                print(f"Failures occurred.")
                has_failures = True

                for failedcase, reason in r.expectedFailures:
                    print(f"---------------------------------------------------------------")
                    print(f"Test case {failedcase} was expected to fail:")
                    print(reason)
                    print(f"---------------------------------------------------------------")

                for failedcase, reason in r.failures:
                    print(f"---------------------------------------------------------------")
                    print(f"Test case {failedcase} failed:")
                    print(reason)
                    print(f"---------------------------------------------------------------")

                for failedcase, reason in r.errors:
                    print(f"---------------------------------------------------------------")
                    print(f"Test case {failedcase} failed with errors:")
                    print(reason)
                    print(f"---------------------------------------------------------------")

            pyjion.disable()
            gc.collect()

    return has_failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pyjion smoke tests")
    parser.add_argument('-f', '--fromfile', metavar='FILE',
                               help='read names of tests to run from a file.')
    parser.add_argument('-o', '--opt-level', type=int,
                       default=1,
                       help='target optimization level')
    parser.add_argument('--pgc', action='store_true', help='Enable PGC')
    args = parser.parse_args()
    main(args.fromfile, args.opt_level, args.pgc)
