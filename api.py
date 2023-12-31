import pandas as pd
import argparse
import requests
import json
import time
from datetime import date
import os

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', dest='f')
args = parser.parse_args()

dest_dir = f"data/{date.today()}"
os.makedirs(dest_dir, exist_ok=True)

df = pd.read_csv(args.f)
emails = list(df['Email'].values)
slugs = [x.split('/')[-1] for x in df['trailhead-url'].values]

def call_api(email, slug):
    try:

        payload2 = {
            "operationName": "GetTrailheadRank",
            "variables": {
                "hasSlug": True,
                "slug": slug
            },
            "query": "fragment TrailheadRank on TrailheadRank {\n  __typename\n  title\n  requiredPointsSum\n  requiredBadgesCount\n }\n\nfragment PublicProfile on PublicProfile {\n  __typename\n  trailheadStats {\n    __typename\n    earnedPointsSum\n    earnedBadgesCount\n    completedTrailCount\n    rank {\n      ...TrailheadRank\n    }\n }\n}\n\nquery GetTrailheadRank($slug: String, $hasSlug: Boolean!) {\n  profile(slug: $slug) @include(if: $hasSlug) {\n    ... on PublicProfile {\n      ...PublicProfile\n    }\n    ... on PrivateProfile {\n      __typename\n    }\n  }\n}\n"
        }
        r = requests.post('https://profile.api.trailhead.com/graphql', json = payload2)
        json_obj = json.loads(r.text)
        details = [email, json_obj['data']['profile']['trailheadStats']['earnedPointsSum'],
            json_obj['data']['profile']['trailheadStats']['earnedBadgesCount'],
            json_obj['data']['profile']['trailheadStats']['completedTrailCount']]
        
        payload3 = {
            "operationName": "GetEarnedSkills",
            "variables": {
                "slug": slug,
                "hasSlug": True
            },
            "query": "fragment EarnedSkill on EarnedSkill {\n  __typename\n  earnedPointsSum\n  id\n  itemProgressEntryCount\n  skill {\n    __typename\n    apiName\n    id\n    name\n  }\n}\n\nquery GetEarnedSkills($slug: String, $hasSlug: Boolean!) {\n  profile(slug: $slug) @include(if: $hasSlug) {\n    __typename\n    ... on PublicProfile {\n      id\n      earnedSkills {\n        ...EarnedSkill\n      }\n    }\n  }\n}\n"
        }
        r = requests.post('https://profile.api.trailhead.com/graphql', json = payload3)
        json_obj = json.loads(r.text)
        skills = [[email, skill['skill']['name'], skill['earnedPointsSum']] for  skill in json_obj['data']['profile']['earnedSkills']]

        cont = True
        after = None
        badges = {}

        while cont:
            payload4 = {
                "operationName": "GetTrailheadBadges",
                "variables": {
                    "count": 24,
                    "after": after,
                    "filter": None,
                    "hasSlug": True,
                    "slug": slug
                },
                "query": "fragment EarnedAward on EarnedAwardBase {\n  __typename\n  id\n  award {\n    __typename\n    id\n    title\n    type\n}\n}\n\nfragment EarnedAwardSelf on EarnedAwardSelf {\n  __typename\n  id\n  award {\n    __typename\n    id\n    title\n    type\n    icon\n    content {\n      __typename\n      webUrl\n      description\n    }\n  }\n  earnedAt\n  earnedPointsSum\n}\n\nfragment StatsBadgeCount on TrailheadProfileStats {\n  __typename\n  earnedBadgesCount\n  superbadgeCount\n}\n\nfragment ProfileBadges on PublicProfile {\n  __typename\n  trailheadStats {\n    ... on TrailheadProfileStats {\n      ...StatsBadgeCount\n    }\n  }\n  earnedAwards(first: $count, after: $after, awardType: $filter) {\n    edges {\n      node {\n        ... on EarnedAwardBase {\n          ...EarnedAward\n        }\n        ... on EarnedAwardSelf {\n          ...EarnedAwardSelf\n        }\n      }\n    }\n    pageInfo {\n      ...PageInfoBidirectional\n    }\n  }\n}\n\nfragment PageInfoBidirectional on PageInfo {\n  __typename\n  endCursor\n  hasNextPage\n  startCursor\n  hasPreviousPage\n}\n\nquery GetTrailheadBadges($slug: String, $hasSlug: Boolean!, $count: Int = 8, $after: String = null, $filter: AwardTypeFilter = null) {\n  profile(slug: $slug) @include(if: $hasSlug) {\n    __typename\n    ... on PublicProfile {\n      ...ProfileBadges\n    }\n  }\n}\n"
            }

            r = requests.post('https://profile.api.trailhead.com/graphql', json = payload4)
            json_obj = json.loads(r.text)
            after = json_obj['data']['profile']['earnedAwards']['pageInfo']['endCursor']
            cont = json_obj['data']['profile']['earnedAwards']['pageInfo']['hasNextPage']
            
            for award in json_obj['data']['profile']['earnedAwards']['edges']:
                if award['node']['award'] == None: continue
                if award['node']['award']['type'] not in badges:
                    badges[award['node']['award']['type']] = []
                badges[award['node']['award']['type']].append(award['node']['award']['title'])
                
        badges_norm = [[email, k, x] for k,v in badges.items() for x in v ]

        return details, skills, badges_norm
    except:
        print('ERROR', end=" ")
        return [], [], []
            
details_header = ['email', 'points', 'badges', 'trails']
skills_header = ['email', 'skillname', 'points']
badges_header = ['email', 'type', 'badgename']

detail_list = []
skill_list = []
badge_list = []

for email,slug in zip(emails, slugs):
    d,s,b = call_api(email, slug)
    detail_list.extend(d)
    skill_list.extend(s)
    badge_list.extend(b)
    print(email, len(badge_list))
    
detail_list = [detail_list[x:x+4] for x in range(0,len(detail_list),4)]
pd.DataFrame(detail_list, index=None, columns=details_header).to_csv(f"{dest_dir}/{date.today()}_details.csv")
pd.DataFrame(skill_list, index=None, columns=skills_header).to_csv(f"{dest_dir}/{date.today()}_skills.csv")
pd.DataFrame(badge_list, index=None, columns=badges_header).to_csv(f"{dest_dir}/{date.today()}_badges.csv")