import requests, traceback
from mgs import MGSPiracy
from argparse import ArgumentParser
from jstate import JState


def send(text: str, token: str, chat_id: int):
    r = requests.post('https://api.telegram.org/bot%s/sendMessage' % token, data={
        'chat_id': chat_id,
        'text': text
    })
    if r.status_code != 200:
        print('error: telegram returned code %d' % r.status_code)


if __name__ == '__main__':
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('--state-file', required=True)
    parser.add_argument('--token', help='Telegram bot token', required=True)
    parser.add_argument('--chat-id', type=int, help='Telegram chat id (with bot)', required=True)
    parser.add_argument('--from', type=int, default=1, help='First page', dest='_from')
    parser.add_argument('--to', type=int, default=5, help='Last page')
    parser.add_argument('--domains', nargs='+', required=True)
    args = parser.parse_args()

    try:
        # get recent cases
        mgs = MGSPiracy(from_page=args._from, to_page=args.to)
        cases = mgs.get_cases()

        # read state
        jst = JState(args.state_file, default=dict(cases=[]))
        data = jst.read()

        # loop through cases
        results = []
        for case in cases:
            if case['statement_number'] in data['cases']:
                continue

            matched = False
            for mydomain in args.domains:
                if mydomain in case['decision_text']:
                    matched = True
                    results.append('%s found in %s' % (mydomain, case['statement_number']))
                    data['cases'].append(case['statement_number'])

                if matched:
                    break

        # remember found cases
        jst.write(data)

        # if found anything, send to telegram
        if results:
            text = '\n'.join(results)
            text = 'new mos-gorsud findings:\n' + text

            send(text=text, token=args.token, chat_id=args.chat_id)
    except Exception as e:
        send(text='error: '+traceback.format_exc(), token=args.token, chat_id=args.chat_id)