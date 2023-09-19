import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List
import csv
import time


@dataclass
class Car:
    link: str
    full_name: str
    description: str
    year: int
    mileage_km: str
    engine_capacity: str
    fuel_type: str
    price_pln: int


class OtomotoScraper:
    def __init__(self, car_make: str) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.11 (KHTML, like Gecko) "
            "Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        self.car_make = car_make
        self.website = f"https://suchen.mobile.de/fahrzeuge/search.html?dam=0&isSearchRequest=true&ms={self.car_make}%3B%3B%3B&pageNumber="

    def scrape_pages(self, number_of_pages: int) -> List[Car]:
        cars = []
        for i in range(1, number_of_pages + 1):
            current_website = f"{self.website}{i}"
            new_cars = self.scrape_cars_from_current_page(current_website)
            if new_cars:
                cars.extend(new_cars)
            time.sleep(20)
        return cars

    def scrape_cars_from_current_page(self, current_website: str) -> List[Car]:
        try:
            response = requests.get(current_website, headers=self.headers)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            soup = BeautifulSoup(response.text, "html.parser")
            cars = self.extract_cars_from_page(soup)

            return cars
        except requests.exceptions.RequestException as e:
            print(f"Problem with scraping website: {current_website}, reason: {e}")
            return []

    def extract_cars_from_page(self, soup: BeautifulSoup) -> List[Car]:
        list_of_cars = []
        try:
            offers_table = soup.find("div", class_="Box cBox--content cBox--resultList")
            cars = offers_table.find_all(
                "div", class_="cBox-body cBox-body--resultitem"
            )
            for car in cars:
                link = car.find(
                    "a", class_="link--muted no--text--decoration result-item"
                )["href"]
                full_name = (
                    car.find("div", class_="headline-block u-margin-bottom-9")
                    .find("span", class_="h3 u-text-break-word")
                    .text
                )
                list_of_cars.append(Car(link=link, full_name=full_name))
        except AttributeError as e:
            print(f"Error in extracting car information: {e}")
        return list_of_cars


def write_to_csv(cars: List[Car]) -> None:
    with open("cars.csv", mode="w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "link",
            "full_name",
            "description",
            "year",
            "mileage_km",
            "engine_capacity",
            "fuel_type",
            "price_pln",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for car in cars:
            writer.writerow(asdict(car))


def scrape_otomoto() -> None:
    make = "17200"
    scraper = OtomotoScraper(make)
    cars = scraper.scrape_pages(3)
    write_to_csv(cars)


if __name__ == "__main__":
    scrape_otomoto()
