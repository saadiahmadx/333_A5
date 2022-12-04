import sys
import argparse
import registrar

def main(args):
    try:
        registrar.app.run(host='0.0.0.0', port=args.port, debug=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='The registrar application',
        allow_abbrev=False, exit_on_error=True)

    parser.add_argument('port', metavar='port',type=int,
        help='the port at which the server should listen')

    main(parser.parse_args())
