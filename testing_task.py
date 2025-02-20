import aiohttp
import asyncio
import json
from datetime import datetime
from uuid import uuid4
import re


class RickAndMortyClient:
    """Client to interact with the Rick and Morty API."""
    BASE_URL = "https://rickandmortyapi.com/api"

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def _fetch_data(self, url):
        async with self.session.get(url) as response:
            return await response.json()

    async def get_characters(self):
        return await self._fetch_data(f"{self.BASE_URL}/character")

    async def get_locations(self):
        return await self._fetch_data(f"{self.BASE_URL}/location")

    async def get_all_episodes(self):
        """Fetch all episodes from the API, handling pagination."""
        episodes = []
        url = f"{self.BASE_URL}/episode"

        while url:
            data = await self._fetch_data(url)
            episodes.extend(data.get("results", []))
            url = data.get("info", {}).get("next")

        return {"results": episodes}

    async def close(self):
        await self.session.close()


async def save_to_json(data, filename):
    formatted_data = [{"id": str(uuid4()), "RawData": item} for item in data["results"]]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(formatted_data, file, indent=4)


async def main():
    client = RickAndMortyClient()

    # Fetch Data from API
    characters = await client.get_characters()
    locations = await client.get_locations()
    episodes = await client.get_all_episodes()

    # Save Data to JSOn files.
    await save_to_json(characters, "characters.json")
    await save_to_json(locations, "locations.json")
    await save_to_json(episodes, "episodes.json")

    episodes_list = episodes["results"]

    # Ensure air_date is in a consistent format
    filtered_episodes = [
        ep["name"]
        for ep in episodes_list
        if (air_date := ep.get("air_date"))
        and (parsed_date := datetime.strptime(air_date, "%B %d, %Y"))
        and 2017 <= parsed_date.year <= 2021
    ]

    print("Episodes between 2017 and 2021 is:")
    for ep in filtered_episodes:
        print(ep)

    print(f"Total episodes is: {len(filtered_episodes)}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())

