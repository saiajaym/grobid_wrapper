import tei_dataclasses
from bs4 import BeautifulSoup

def elem_to_text(elem, default=''):
    if elem:
        return elem.getText(separator=' ', strip=True)
    else:
        return default

class TEIFile(object):
    def _init_(self, filename):
        self.filename = filename
        self.soup = self.read_tei(filename)
        self._text = ''
        self._title = ''
        self._abstract = ''
        self._body = ''
        self._keywords=[]
        self._subsections = {}
        self._journal=''

    
    def read_tei(self, tei_file):
        with open(tei_file, 'r') as tei:
            soup = BeautifulSoup(tei, 'lxml')
            return soup
        raise RuntimeError('Cannot generate a soup from the input')
        

    @property
    def doi(self):
        idno_elem = self.soup.find('idno', type='DOI')
        if not idno_elem:
            return ''
        else:
            return idno_elem.getText()
        

    @property
    def title(self):
        if not self._title:
            if self.soup.title:
                self._title = self.soup.title.getText(separator=' ', strip=True)
        return self._title

    @property
    def abstract(self):
        if not self._abstract:
            abstract = elem_to_text(self.soup.abstract)
            self._abstract = abstract
        return self._abstract
    
    @property
    def body(self):
        if not self._body:
            body = elem_to_text(self.soup.body)
            self._body = body
        return self._body

    @property
    def authors(self):
        if not self.soup.analytic or not self.soup.analytic.find_all('author'):
            return ''
        authors_in_header = self.soup.analytic.find_all('author')

        result = []
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            email = elem_to_text(author.find("email"))
            aff = author.find("affiliation")
            if aff:
                rawaff = elem_to_text(aff.find("note", type="raw_affiliation"))
                institution = elem_to_text(aff.find("orgName", type = "institution"))
                department = elem_to_text(aff.find("orgName", type = "department"))
                country =elem_to_text(aff.find("country"))
                affiliation  = Affiliation(rawaff, department=department, institution=institution, country=country)
            else:
                affiliation=Affiliation('','','','')
            person = Author(firstname, middlename, surname, email, affiliation)
            result.append(person)
        return result
    
    @property
    def text(self):
        if not self._text:
            if not self.soup.body or not self.soup.body.find_all("div"):
                return ''
            divs_text = []
            for div in self.soup.body.find_all("div"):
                # div is neither an appendix nor references, just plain text.
                if not div.get("type"):
                    div_text = div.get_text(separator=' ', strip=True)
                    divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text
        return self._text
    @property
    def conclusion(self):
        if not self.soup.body or not self.soup.body.find_all("div"):
            return ''
        for div in self.soup.body.find_all("div"):
             if not div.get("type"):
                if 'Conclusion' in div.getText(separator=' '):
                    return div.getText(separator=' ')
                
    @property
    def acknowledgement(self):
        div=[]
        """for div in self.soup.body.find_all("div"):
             if not div.get("type"):
                if 'acknowledg' in div.getText(separator=' ').lower():
                    return div.getText(separator=' ')"""
        div =elem_to_text(self.soup.find("div", type = "acknowledgement"))
        if div:
            return div
        elif self.soup.body and self.soup.body.find_all("div"):
            for div in self.soup.body.find_all("div"):
                if not div.get("type"):
                    if 'Acknowledgment' in div.getText(separator=' ').lower():
                        return div.getText(separator=' ')
        else:
            return ''
    @property
    def introduction(self):
        div=[]
        if not self.soup.body or not self.soup.body.find_all("div"):
            return ''
        for div in self.soup.body.find_all("div"):
             if not div.get("type"):
                if 'Introduction' in div.getText(separator=' ').lower():
                    return div.getText(separator=' ')
    
    @property
    def keywords(self):
        key = self.soup.find("keywords")
        if key:
            if key.find("terms"):
                _keywords = [elem_to_text(i) for i in key.find_all("term")]
            else:
                self._keywords = elem_to_text(key)
        return self._keywords
    
    
    @property
    def journal(self):
        meta = self.soup.find("teiheader")
        if meta:
            meta = meta.find("monogr")
            if meta:
                journ = elem_to_text(meta.find("title", {"level":"j","type":"main"}))
                issn = elem_to_text(meta.find("idno",{"type":"ISSN"}))
                publisher = elem_to_text(meta.find("publisher"))
                date=''
                if meta.find("date") and 'when' in meta.find("date").attrs:
                    date = meta.find("date").attrs['when']
                self._journal= Journal(title=journ, issn=issn, publisher=publisher, date=date)
                return self._journal
        return ''
    
    @property
    def references(self):
        li=[]
        refs=[]
        ref = self.soup.find("div", type="references")
        if ref:
            for i in ref.find_all("biblstruct"):
                li=[]
                title = elem_to_text(i.find("title"))
                for au in i.find_all("author"):
                    persname=au.persname
                    if au.persname:
                        firstname = elem_to_text(persname.find("forename", type="first"))
                        middlename = elem_to_text(persname.find("forename", type="middle"))
                        surname = elem_to_text(persname.surname)
                        person = Author(firstname, middlename, surname, '', None)
                        li.append(person)
                date=''
                if i.find("date") and 'when' in i.find("date").attrs:
                    date = i.find("date").attrs['when']
                pubplace = elem_to_text(i.find("pubplace"))
                resp = elem_to_text(i.find("respstmt"))
                note = elem_to_text(i.find("note"))
                raw_ref = elem_to_text(i.find("note", type="raw_reference"))
                publisher = elem_to_text(i.find("publisher"))
                refs.append(Reference( title= title, authors=li, rawreference=raw_ref, publiher=publisher,pubplace=pubplace,date=date,respstmt=resp))
        return refs
    @property
    def id(self):
        base_name = basename(self.filename)
        stem, ext = splitext(base_name)
        return stem[0:-4]
