"""
FoodData Central API: https://fdc.nal.usda.gov/api-guide.html
"""
import asyncio
import os

import aiohttp
from pydantic import BaseModel, validator

from models import AbridgedFoodItem

FOOD_DATA_API_KEY = os.getenv("FOOD_DATA_API_KEY")


class FoodInfo(BaseModel):
    food: str
    mass: float
    database: str = "US Food Central"
    energy: float | None = None
    protein: float | None = None
    carbohydrates: float | None = None
    sugar: float | None = None
    fats: float | None = None
    saturated_fat: float | None = None
    cholesterol: float | None = None
    vitamin_c: float | None = None
    fe: float | None = None
    ca: float | None = None

    @validator('*')
    def round_floats(cls, v):
        """Round float number, so we don't get 0.11900000000000001"""
        if isinstance(v, float):
            return round(v, 3)
        return v

    def __str__(self):
        """Comma separated string representation."""
        return ",".join(
            map(
                str,
                (
                    '"' + self.food + '"',
                    self.mass,
                    '"' + self.database + '"',
                    self.energy,
                    self.protein,
                    self.carbohydrates,
                    self.sugar,
                    self.fats,
                    self.saturated_fat,
                    self.cholesterol,
                    self.vitamin_c,
                    self.fe,
                    self.ca,
                ),
            )
        ).replace("None", "")

    class Config:
        validate_assignment = True


async def calculate_food_nutrients(fdc_id: str, portion: float) -> FoodInfo:
    """
    Calculate food nutrients of food item with specified FDC ID and mass.

    :param fdc_id: FDC ID from FoodData Central
    :param portion: Mass of portion, in grams
    :return: information about food item
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}",
            params={"api_key": FOOD_DATA_API_KEY, "format": "abridged"},
        ) as resp:
            resp.raise_for_status()
            text = await resp.text()

    # with open('response.json', 'w') as f:
    #     f.write(response.text)
    # food_item = InlineResponse200.parse_raw(response.text)
    #
    # with open('response.json', 'r') as f:
    #     raw = f.read()
    # food_item = InlineResponse200.parse_raw(raw).__root__
    # food_item = AbridgedFoodItem.parse_raw(raw)
    food_item = AbridgedFoodItem.parse_raw(text)

    food_info = FoodInfo(food=food_item.description.strip(), mass=portion)
    multiplier = portion / 100

    for nutrient in food_item.food_nutrients:
        match nutrient.number:
            case "208" | "957":
                food_info.energy = nutrient.amount * multiplier
            case "203":
                food_info.protein = nutrient.amount * multiplier
            case "205":
                food_info.carbohydrates = nutrient.amount * multiplier
            case "269":
                food_info.sugar = nutrient.amount * multiplier
            case "205":
                food_info.carbohydrates = nutrient.amount * multiplier
            case "204":
                food_info.fats = nutrient.amount * multiplier
            case "606":
                food_info.saturated_fat = nutrient.amount * multiplier
            case "601":
                food_info.cholesterol = nutrient.amount * multiplier
            case "401":
                food_info.vitamin_c = nutrient.amount * multiplier
            case "303":
                food_info.fe = nutrient.amount * multiplier
            case "301":
                food_info.ca = nutrient.amount * multiplier

    return food_info


async def main():
    info = await calculate_food_nutrients("1900168", 100)
    print(info)


if __name__ == "__main__":
    asyncio.run(main())
