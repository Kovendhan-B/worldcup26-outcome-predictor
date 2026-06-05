"""Country flag images for all FIFA World Cup 2026 teams."""

# ISO 3166-1 alpha-2 codes for flagcdn.com
COUNTRY_CODES = {
    "Algeria": "dz",
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Bosnia and Herzegovina": "ba",
    "Brazil": "br",
    "Canada": "ca",
    "Cape Verde": "cv",
    "Colombia": "co",
    "Croatia": "hr",
    "Curaçao": "cw",
    "Czech Republic": "cz",
    "DR Congo": "cd",
    "Ecuador": "ec",
    "Egypt": "eg",
    "England": "gb-eng",
    "France": "fr",
    "Germany": "de",
    "Ghana": "gh",
    "Haiti": "ht",
    "Iran": "ir",
    "Iraq": "iq",
    "Ivory Coast": "ci",
    "Japan": "jp",
    "Jordan": "jo",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Norway": "no",
    "Panama": "pa",
    "Paraguay": "py",
    "Portugal": "pt",
    "Qatar": "qa",
    "Saudi Arabia": "sa",
    "Scotland": "gb-sct",
    "Senegal": "sn",
    "South Africa": "za",
    "South Korea": "kr",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Tunisia": "tn",
    "Turkey": "tr",
    "United States": "us",
    "Uruguay": "uy",
    "Uzbekistan": "uz",
}

FLAG_CDN = "https://flagcdn.com/w40"


def flag(team_name):
    """Return HTML img tag + team name for markdown display."""
    code = COUNTRY_CODES.get(team_name)
    if code:
        return (
            f'<img src="{FLAG_CDN}/{code}.png" '
            f'width="24" height="16" '
            f'style="vertical-align:middle; margin-right:6px; '
            f'border-radius:2px;">'
            f'{team_name}'
        )
    return team_name


def flag_label(team_name):
    """Return plain text label with country code for selectboxes."""
    code = COUNTRY_CODES.get(team_name, "")
    if code:
        return f"[{code.upper()}] {team_name}"
    return team_name
