import requests, textract, re, os, tempfile, random, string, csv
from argparse import ArgumentParser
from bs4 import BeautifulSoup

headers = {
    'Referer': 'https://mos-gorsud.ru/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
}

regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


def strgen(n: int) -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n)).lower()


class MosGorSud:
    def __init__(self, url: str, upto_pages: int, output: str):
        self.url = url
        self.upto_pages = upto_pages
        self.output = output

    def go(self):
        f = open(self.output, 'w', newline='')
        csv_writer = csv.writer(f)

        for page in range(1, self.upto_pages):
            print(f'page {page}')

            url = self.url + '?page=' + str(page)
            r = requests.get(url, headers=headers)

            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select('.searchResultContainer table.custom_table tbody tr')

            for row in rows:
                cols = row.find_all('td')

                date = cols[0].get_text().strip()
                statement_number = cols[1].get_text().strip()
                applicant = cols[3].get_text().strip()
                objects = cols[4].get_text().strip()
                link = self.full_link(cols[5].find('a')['href'])

                text = mgs.get_document_text(link)
                links = '\n'.join(mgs.get_links(text))

                # print(f'date={date}, stmt_number={statement_number}, applicant={applicant} objects={objects} link={link}')

                csv_writer.writerow((date, statement_number, applicant, objects, link, links))

        f.close()

    def full_link(self, url: str) -> str:
        if not url.startswith('http:') and not url.startswith('https:'):
            if not url.startswith('/'):
                url = '/' + url
            url = 'https://mos-gorsud.ru' + url
        return url

    def get_document_text(self, url: str) -> str:
        print(f'downloading {url}')

        r = requests.get(url, allow_redirects=True, headers=headers)
        content_disposition = r.headers['Content-Disposition']
        filename, file_extension = os.path.splitext(re.search('attachment; filename="(.*?)"', content_disposition).group(1))

        tempname = '%s/%s%s' % (tempfile.gettempdir(), strgen(10), file_extension)

        with open(tempname, 'wb') as f:
            f.write(r.content)

        text = textract.process(tempname).decode('utf-8')
        os.unlink(tempname)

        return text

    def get_links(self, s: str) -> list[str]:
        return list(set(re.findall(regex, s)))


if __name__ == '__main__':
    argp = ArgumentParser()
    argp.add_argument('--output', type=str, default='output.csv',
                      help='CSV output file name')
    argp.add_argument('--upto-pages', type=int, default=10,
                      help='Last page to parse')
    args = argp.parse_args()

    mgs = MosGorSud(url="https://mos-gorsud.ru/mgs/defend",
                    upto_pages=args.upto_pages,
                    output=args.output)
    mgs.go()