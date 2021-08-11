import random

birthday_wishes = [
    "We wish you an amazing year that ends with accomplishing all the great goals that you have set!",
    "The warmest wishes to a great member of our alumni family. May your special day be full of happiness, fun and cheer!",
    "Today is a great day to get started on another 365-day journey. It’s a fresh start to new beginnings, new hopes, and great endeavors. Besides, be sure to have adventures along the way. Wishing you the best of today and every day in the future!",
    "Hoping that this birthday is the start of an amazing year where you accomplish every goal and shatter every record there is to break. Enjoy your birthday!",
    "May this birthday bring the milestones you have to achieve, dreams you have to fulfill, and horizons you have to conquer. Wishing you a happy birthday from every member of our team!",
    "This day is momentous, considering that you circumvented the sun once more. May this signify a series of greats for you- a great day, a great year, a great life. Thus, put on a smile and enjoy this day to the fullest. Happy Birthday!",
    "May this birthday bring auspiciousness and joy to you forever. We pray for your long life. May the Lord always protect you. By noble deeds, may you attain fame, and may your life be fulfilled.",
    "Here is a wish for your birthday. May you receive whatever you ask for, may you find whatever you seek. Happy birthday!",
]


def return_random_message():
    return random.choice(birthday_wishes)
