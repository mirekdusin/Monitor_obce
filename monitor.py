import requests
from collections import defaultdict
from csv import reader
from bs4 import BeautifulSoup


def print_missing(ico):
    print(ico + ",NULL")


def get_data_from_monitor(ico, data_labels, rad, rok, vykaz):
    url = "https://monitor.statnipokladna.cz/api/monitorws"
    headers = {'content-type': 'text/xml'}
    body = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Header/>
        <soap:Body>
            <req:MonitorRequest
                xmlns:req="urn:cz:mfcr:monitor:schemas:MonitorRequest:v1"
                xmlns:mon="urn:cz:mfcr:monitor:schemas:MonitorTypes:v1">
                <req:Hlavicka>
                    <mon:OrganizaceIC>""" + ico + """</mon:OrganizaceIC>
                    <mon:Rok>""" + rok + """</mon:Rok>
                    <mon:Vykaz>""" + vykaz + """</mon:Vykaz>
                    <mon:Rad>""" + rad + """</mon:Rad>
                </req:Hlavicka>
            </req:MonitorRequest>
        </soap:Body>
    </soap:Envelope>"""

    data_buffer = {}
    data_buffer = defaultdict(lambda: 0, data_buffer)

    response = requests.post(url, data=body, headers=headers)
    xml = BeautifulSoup(response.content, 'xml')

    vydaje_rozpoctove = xml.find('fin212m:VydajeRozpoctove')

    if vydaje_rozpoctove:
        vydaje_radky = vydaje_rozpoctove.find_all('fin212m:Radek')
        if vydaje_radky:
            for row in vydaje_radky:
                paragraf = row.find('fin212m:Paragraf')
                if paragraf:
                    vysledek = row.find('fin212m:Vysledek')
                    if vysledek:
                        data_buffer[paragraf.text] = data_buffer[paragraf.text] + float(vysledek.text)
                    else:
                        print_missing(ico)
                else:
                    print_missing(ico)
            print(ico + ",", end='')
            for label in data_labels:
                print(str(data_buffer[label]) + ",", end='')
            print("")
        else:
            print_missing(ico)
    else:
        print_missing(ico)


data_labels = ["2122", "3721", "3722", "3723", "3724", "3725", "3726", "3727", "3728", "3729"]
rad = "1"  #1 jednotky, 1000 tisice...
rok = "2019"
vykaz = "051"  #plneni rozpoctu USC

with open('ico.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    for row in csv_reader:
        get_data_from_monitor(row[0], data_labels, rad, rok, vykaz)

