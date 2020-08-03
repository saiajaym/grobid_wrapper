from dataclasses import dataclass
from os.path import basename, splitext


@dataclass
class Affiliation:
    rawaffiliation: str
    department: str
    institution: str
    country: str

        
@dataclass
class Author:
    firstname: str
    middlename: str
    surname: str
    email: str
    affiliation: Affiliation
        
@dataclass
class Journal:
    title: str
    issn: str
    publisher: str
    date: str
        
@dataclass
class Reference:
    title: str
    authors: list
    rawreference: str
    publiher: str
    pubplace: str
    date: str
    respstmt: str
