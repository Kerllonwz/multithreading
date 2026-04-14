import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://havokkmorands.github.io"


def extract_movies():
    """Coleta os links de todos os filmes na página principal."""
    url = f"{BASE_URL}/movie-catalog/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for tag in soup.select("a[data-testid='movie-link']"):
        href = tag.get("href")
        if href:
            links.append(BASE_URL + href)

    return links


def extract_movie_details(url):
    """Coleta nome, data de lançamento, nota e sinopse de um filme."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.select_one("[data-testid='movie-title']")
    release = soup.select_one("[data-testid='movie-release']")
    rating = soup.select_one("[data-testid='movie-rating']")
    synopsis = soup.select_one("[data-testid='movie-synopsis']")

    return {
        "nome": title.get_text(strip=True) if title else "",
        "data_de_lancamento": release.get_text(strip=True).replace("Lançamento:", "").strip() if release else "",
        "nota": rating.get_text(strip=True).replace("Nota:", "").strip() if rating else "",
        "sinopse": synopsis.get_text(strip=True).replace("Sinopse:", "").strip() if synopsis else "",
    }


def main():
    print("Coletando links dos filmes...")
    movie_links = extract_movies()
    print(f"{len(movie_links)} filmes encontrados.")

    print("Buscando detalhes com multithreading...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        movies = list(executor.map(extract_movie_details, movie_links))

    output_path = "movies.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nome", "data_de_lancamento", "nota", "sinopse"])
        writer.writeheader()
        writer.writerows(movies)

    print(f"Arquivo '{output_path}' gerado com {len(movies)} filmes.")


if __name__ == "__main__":
    main()
