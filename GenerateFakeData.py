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
    
    # Monthly units sold based on months since release
    if platform == 'ACX Royalty Share':
        # Royalty Share books tend to have lower sales
        if months_since_release < 1:
            monthly_units = random.randint(10, 80)
        elif months_since_release < 3:
            monthly_units = random.randint(30, 150)
        elif months_since_release < 6:
            monthly_units = random.randint(50, 250)
        else:
            monthly_units = random.randint(60, 300)
    else:
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
    narrators = [
    "Jason Clarke", "Samantha Prescott", "Ava Winters",
    "Taylor James", "Rachel Scott", "AI Narrator"
    ]
    narrator = random.choice(narrators)
    narrator_split = False # Default to no split unless specified by platform logic
    # Production cost logic
    if platform == 'ACX Royalty Share':
        narrator_split = random.random() < 0.4  # 40% chance of narrator split
    
    if narrator == "AI Narrator":
        if random.random() < 0.4:
            prod_cost = 0  # Using Amazon Virtual Voice or free AI beta
            uses_amazon_ai = True
        else:
            prod_cost = random.uniform(100, 1500)
            uses_amazon_ai = True
    else:
        uses_amazon_ai = False
        if narrator in ["Jason Clarke", "Samantha Prescott", "Ava Winters"]:
            prod_cost = random.uniform(4000, 8000)  # High-end narrators
        else:
            prod_cost = random.uniform(2000, 4000)  # Mid-range narrators

    # Increase production cost for ACX Royalty Share
    if platform == 'ACX Royalty Share':
        prod_cost *= random.uniform(1.1, 1.5)  # 10-50% more expensive

    # Simulate payout logic
    if platform == 'ACX Exclusive':
        royalty_rate = 0.40
    elif platform == 'ACX Royalty Share':
        # Lower and more variable royalty rate for Royalty Share
        if narrator_split:
            royalty_rate = round(random.uniform(0.10, 0.18), 3)
        else:
            royalty_rate = round(random.uniform(0.18, 0.25), 3)
    elif platform == 'Findaway':
        royalty_rate = round(random.uniform(0.30, 0.45), 3) # realistic range
    elif platform == 'BookFunnel':
        royalty_rate = 1.00
    elif platform == 'Spotify' and random.random() < 0.3:  # 30% chance of bad month
        royalty_rate = round(random.uniform(0.30, 0.50), 3)  # subscription payout range
    else:
        royalty_rate = round(random.uniform(0.30, 0.50), 3)  # catch-all ACYL rate

    # Override for narrator-split low-royalty books
    if royalty_rate < 0.25 and narrator_split:
        if random.random() < 0.05:  # 5% chance of low sales
            monthly_units = random.randint(500, 800)
        else:
            monthly_units = random.randint(20, 300)
            
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
    if monthly_earnings <= 0 and prod_cost == 0:
        months_to_break_even = 0
    elif royalty_rate < 0.15 or monthly_earnings <= 0:
        months_to_break_even = "Unknown"
    else:
        months_to_break_even = prod_cost / monthly_earnings

    break_even_date = pd.to_datetime(release_date) + pd.DateOffset(months=int(months_to_break_even)) if isinstance(months_to_break_even, (int, float)) else "Unknown"
    if months_to_break_even == 0:
        break_even_status = "Already Profitable"
    elif months_to_break_even == "Unknown":
        break_even_status = "Unclear - No Earnings Yet"
    elif royalty_rate < 0.20 and monthly_units < 100:
        break_even_status = "Unlikely"
    elif months_to_break_even > months_since_release:
        break_even_status = "In Progress"
    else:
        break_even_status = "Broken Even"

    loss_leader = royalty_rate < 0.20 and monthly_units < 100 and not has_broken_even
    risky_combo = (
        royalty_rate < 0.35
        and narrator_split == True
        and prod_cost > 5000
    )
    overachiever = (
        royalty_rate >= 0.50
        and monthly_units > 700
        and months_to_break_even != "Unknown"
        and months_to_break_even < 2
        and months_since_release <= 3
    )

    # Add a flag for ACX Royalty Share risk
    acx_royalty_share_risk = (
        platform == 'ACX Royalty Share'
        and (royalty_rate < 0.18 or prod_cost > 5000 or not has_broken_even)
    )

    return {
        'Author': fake.name(),
        'Book Title': fake.sentence(nb_words=4),
        'Audiobook Release Date': release_date,
        'New Release Boost': new_release_boost,
        'Months Since Release': months_since_release,
        'Platform': platform,
        'Book Price': book_price,
        'Production Cost': prod_cost,
        'Narrator Split': narrator_split,
        'Narrator': narrator,
        'Uses Amazon AI': uses_amazon_ai,
        'Monthly Units': monthly_units,
        'Royalty Rate': royalty_rate,
        'Monthly Earnings': round(monthly_earnings, 2),
        'Est. Months to Break Even': round(months_to_break_even, 1) if isinstance(months_to_break_even, (int, float)) else "Unknown", # based on current earnings
        'Break Even Status': break_even_status,
        'Break Even Date': break_even_date,
        'Loss Leader': loss_leader,
        'Risky Combo': risky_combo,
        'Overachiever': overachiever,
        'ACX Royalty Share Risk': acx_royalty_share_risk
    }

# Create 50 fake entries
data = [generate_fake_royalty_record() for _ in range(50)]
df = pd.DataFrame(data)

# Save to Excel file
df.to_excel('FakeRoyaltyData.xlsx', index=False)