# GenerateFakeData.py
# This script generates fake royalty share data for testing purposes.

from faker import Faker
import random
import pandas as pd
import openpyxl

fake = Faker()

# Function to simulate AYCL royalty payout logic
def simulate_aycl_royalty(monthly_fee=14.95, num_books_listened=5, narrator_split=True):
    """
    Simulates AYCL (All-You-Can-Listen) royalty payout logic.

    :param monthly_fee: The monthly fee paid by the listener.
    :type monthly_fee: float
    :param num_books_listened: The number of books listened to in a month.
    :type num_books_listened: int
    :param narrator_split: Whether the narrator receives a split of the earnings.
    :type narrator_split: bool
    :return: The earnings of the author and narrator, if applicable.
    :rtype: tuple[float, float]
    """
    if num_books_listened <= 0:
        raise ValueError("num_books_listened must be greater than 0")

    # Revenue per book
    revenue_per_book = monthly_fee / num_books_listened
    audible_cut = 0.5  # 50%
    author_narrator_pool = revenue_per_book * (1 - audible_cut)

    if narrator_split:
        author_earning = author_narrator_pool / 2
        narrator_earning = author_narrator_pool / 2
    else:
        author_earning = author_narrator_pool
        narrator_earning = 0

    return round(author_earning, 2), round(narrator_earning, 2)

# Example output
simulate_aycl_royalty(num_books_listened=10, narrator_split=True)
# → (0.75, 0.75)

# Function to generate fake royalty records
def generate_fake_royalty_record():
    platforms = ['ACX Exclusive', 'ACX Royalty Share', 'Findaway', 'BookFunnel', 'Spotify']
    platform = random.choice(platforms)
    
    book_price = round(random.uniform(7.99, 19.99), 2)
    release_date = fake.date_between(start_date='-2y', end_date='today')
    today = pd.to_datetime(pd.Timestamp.today())
    months_since_release = (today - pd.to_datetime(release_date)).days // 30
    if months_since_release < 1:
        monthly_units = random.randint(20, 250)
    elif months_since_release < 3:
        monthly_units = random.randint(100, 500)
    elif months_since_release < 6:
        monthly_units = random.randint(150, 800)
    else:
        monthly_units = random.randint(200, 1000)
    
    # OPTIONAL: Apply a bonus for new releases with launch buzz
    if months_since_release < 1 and random.random() < 0.5:
        monthly_units = int(monthly_units * 1.3)  # 30% boost
    new_release_boost = months_since_release < 1 and random.random() < 0.5
    narrator_split = random.choice([True, False])
    prod_cost = random.randint(1500, 6000)

    # Simulate payout logic
    if platform == 'ACX Exclusive':
        royalty_rate = 0.40
    elif platform == 'ACX Royalty Share':
        royalty_rate = 0.40 / 2 if narrator_split else 0.40
    elif platform == 'Findaway':
        royalty_rate = 0.45
    elif platform == 'BookFunnel':
        royalty_rate = 1.00
    else:
        royalty_rate = 0.50  # Spotify or AYCL assumption

    # Check for division by zero
    if monthly_units == 0:
        royalty_per_sale = 0
        monthly_earnings = 0
    else:
        if narrator_split:
            royalty_rate /= 2  # Split with narrator
        royalty_per_sale = book_price * royalty_rate
        monthly_earnings = monthly_units * royalty_per_sale

    
    # Check for division by zero
    if prod_cost == 0:
        months_to_break_even = "Never"
    else:
        months_to_break_even = prod_cost / monthly_earnings if monthly_earnings > 0 else "Never"

    return {
        'Author': fake.name(),
        'Book Title': fake.sentence(nb_words=4),
        'Audiobook Release Date': release_date,
        'New Release Boost': new_release_boost,
        'Months Since Release': months_since_release,
        'Platform': platform,
        'Book Price': book_price,
        'Narrator Split': narrator_split,
        'Monthly Units': monthly_units,
        'Production Cost': prod_cost,
        'Royalty Rate': royalty_rate,
        'Monthly Earnings': round(monthly_earnings, 2),
        'Months to Break Even': round(months_to_break_even, 1) if months_to_break_even else "Never"
    }

# Create 50 fake entries
data = [generate_fake_royalty_record() for _ in range(50)]
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('FakeRoyaltyData.xlsx', index=False)