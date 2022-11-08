from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import collections, pprint
from pokedex import connectionMongoDB


from typing import List, NamedTuple

def Running (n1,n2):
    scraped_pokemon_data = []

    class Pokemon(NamedTuple):
        id: int
        idpokedex: int
        name: str
        details_path: str
        types: List[str]
        total: int
        hp: int
        attack: int
        defense: int
        sp_attack: int
        sp_defence: int
        speed: int
        imagem: str

    url = 'https://pokemondb.net/pokedex/all'
    request = Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    page = urlopen(request)

    page_content_bytes = page.read().decode("utf-8")
    page_html = page_content_bytes

    soup = BeautifulSoup(page_html, "html.parser")

    pokemon_rows = soup.find_all("table", id="pokedex")[0].find_all('tbody')[0].find_all('tr')
    idlist = []
    id = 0
    for pokemon in pokemon_rows[n1:n2]:
        pokemon_data = pokemon.find_all("td")
        idpokedex = pokemon_data[0]['data-sort-value']
        idlist.append(idpokedex)
        contadorID = collections.Counter(idlist)
        posID = contadorID[(idpokedex)]


        name = pokemon_data[1].find_all("a")[0].getText()
        if pokemon_data[1].find_all("small"):
            name = pokemon_data[1].find_all("small")[0].getText()
        details_uri = pokemon_data[1].find_all('a')[0]['href']

        types = []
        for pokemon_type in pokemon_data[2].find_all("a"):
            types.append(pokemon_type.getText())

        total = pokemon_data[3].getText()
        hp = pokemon_data[4].getText()
        attack = pokemon_data[5].getText()
        defense = pokemon_data[6].getText()
        sp_attack = pokemon_data[7].getText()
        sp_defence = pokemon_data[8].getText()
        speed = pokemon_data[9].getText()

        entry_url = f'https://pokemondb.net{details_uri}'
        request = Request(
            entry_url,
            headers= {'User-Agent': 'Mozilla/5.0'}
        )
        entry_page_html = urlopen(request).read().decode("utf-8")
        entry_soup = BeautifulSoup(entry_page_html,"html.parser")

        try:
            imageLinkOBJ = entry_soup.find_all("div", {'class': "grid-col span-md-6 span-lg-4 text-center"})[posID-1]\
                .find_all('p')[0].find_all('img')[0]
            listaImg = [".png",".jpg"]
            imageLinkString = str(imageLinkOBJ)
            indexLinkStart = imageLinkString.index('http')
            indexLinkEnd = imageLinkString.rindex(listaImg[0])
            imagem = imageLinkString[indexLinkStart:indexLinkEnd + 4]
        except:
            imageLinkOBJ = entry_soup.find_all("div", {'class': "grid-col span-md-6 span-lg-4 text-center"})[posID - 1] \
                .find_all('p')[0].find_all('img')[0]
            imageLinkString = str(imageLinkOBJ)
            indexLinkStart = imageLinkString.index('http')
            indexLinkEnd = imageLinkString.rindex(listaImg[1])
            imagem = imageLinkString[indexLinkStart:indexLinkEnd + 4]


        typed_pokemon = Pokemon(
            id = int(id),
            idpokedex = int(idpokedex),
            name=name,
            details_path=details_uri,
            types=types,
            total=int(total),
            hp=int(hp),
            attack=int(attack),
            defense=int(defense),
            sp_attack=int(sp_attack),
            sp_defence=int(sp_defence),
            speed=int(speed),
            imagem=imagem,
        )

        print(f'Added {name} successfull!')
        scraped_pokemon_data.append(typed_pokemon)
        id = len(scraped_pokemon_data)

        pokemonsData = {
            "_ID": typed_pokemon.id,
            "idpokedex": typed_pokemon.idpokedex,
            "name": typed_pokemon.name,
            "details_path": typed_pokemon.details_path,
            "types": typed_pokemon.types,
            "total": typed_pokemon.total,
            "hp": typed_pokemon.hp,
            "defense": typed_pokemon.defense,
            "sp_attack": typed_pokemon.sp_attack,
            "sp_defence": typed_pokemon.sp_defence,
            "speed": typed_pokemon.speed,
            "imagem": typed_pokemon.imagem,
        }

        connectionMongoDB.pokemon_collection.insert_one(pokemonsData)