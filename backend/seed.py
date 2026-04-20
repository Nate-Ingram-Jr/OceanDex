from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.SeaCreature).count() > 0:
    print("Database already seeded.")
    db.close()
    exit()

# ── States ────────────────────────────────────────────────────────────────────

state_data = [
    {"code": "MD", "name": "Maryland", "coastline": "Atlantic", "primary_body": "Chesapeake Bay"},
    {"code": "DE", "name": "Delaware", "coastline": "Atlantic", "primary_body": "Delaware Bay"},
    {"code": "NJ", "name": "New Jersey", "coastline": "Atlantic", "primary_body": "Atlantic Ocean"},
    {"code": "US", "name": "United States (Federal)", "coastline": "All", "primary_body": None},
]

states = {}
for s in state_data:
    obj = models.State(**s)
    db.add(obj)
    db.flush()
    states[s["code"]] = obj

# ── Regions ───────────────────────────────────────────────────────────────────

region_data = [
    {"state": "MD", "name": "Chesapeake Bay", "water_type": "Estuary", "avg_depth_m": 6.6, "notes": "Largest estuary in the US"},
    {"state": "MD", "name": "Ocean City Atlantic Coast", "water_type": "Coastal", "avg_depth_m": 30.0},
    {"state": "DE", "name": "Delaware Bay", "water_type": "Estuary", "avg_depth_m": 8.9, "notes": "Major horseshoe crab spawning ground"},
    {"state": "DE", "name": "Rehoboth Beach Shelf", "water_type": "Coastal", "avg_depth_m": 25.0},
    {"state": "NJ", "name": "Sandy Hook Bay", "water_type": "Estuary", "avg_depth_m": 4.0},
    {"state": "NJ", "name": "Barnegat Bay", "water_type": "Estuary", "avg_depth_m": 2.0, "notes": "Shallow barrier island lagoon"},
    {"state": "NJ", "name": "NJ Atlantic Shelf", "water_type": "Offshore", "avg_depth_m": 50.0},
]

regions = {}
for r in region_data:
    obj = models.Region(
        state_id=states[r["state"]].id,
        name=r["name"],
        water_type=r["water_type"],
        avg_depth_m=r.get("avg_depth_m"),
        notes=r.get("notes"),
    )
    db.add(obj)
    db.flush()
    regions[r["name"]] = obj

# ── Species ───────────────────────────────────────────────────────────────────

def add_creature(data):
    regs = data.pop("regulations", [])
    region_assocs = data.pop("region_assocs", [])
    conservation = data.pop("conservation", None)

    c = models.SeaCreature(**data)
    db.add(c)
    db.flush()

    if conservation:
        db.add(models.ConservationStatus(creature_id=c.id, **conservation))

    for ra in region_assocs:
        region_name = ra.pop("region")
        db.add(models.RegionCreature(
            creature_id=c.id,
            region_id=regions[region_name].id,
            **ra,
        ))

    for reg in regs:
        state_code = reg.pop("state")
        db.add(models.LegalRegulation(
            creature_id=c.id,
            state_id=states[state_code].id,
            **reg,
        ))

    return c


add_creature({
    "common_name": "Atlantic Blue Crab",
    "scientific_name": "Callinectes sapidus",
    "category": "shellfish",
    "max_length_cm": 23.0,
    "depth_min_m": 0,
    "depth_max_m": 11.0,
    "weight": "Up to 0.9 kg (2 lbs)",
    "diet": "Omnivore — clams, snails, worms, small fish, plant matter",
    "lifespan": "1–3 years",
    "habitat": "Estuaries, brackish bays, coastal waters",
    "migratory": True,
    "about": "The Atlantic blue crab is the icon of the Chesapeake Bay and one of the most commercially valuable shellfish on the East Coast. Named for the vivid blue claws of males, these opportunistic omnivores play a vital role in estuarine food webs. Despite their abundance, populations have declined significantly from historic highs due to a combination of overharvesting, water quality degradation, and habitat loss.",
    "legal_notice": "Recreational and commercial harvest is permitted with appropriate licensing. Egg-bearing (sponge) females must be released immediately.",
    "encounter_tip": "Blue crabs can be caught with crab pots, trot lines, or hand lines. Use bait such as chicken necks or fish heads. Always check local size and bag limits before keeping your catch.",
    "conservation": {
        "iucn_level": "Least Concern",
        "population_trend": "Decreasing",
        "threat_score": 18,
        "aware_fact": "Blue crab populations in the Chesapeake Bay have dropped significantly since the 1990s. A single female crab can produce up to 8 million eggs per year, yet recruitment remains low due to degraded nursery habitat and overharvesting of juveniles.",
        "last_assessed": "2021",
        "main_threats": [
            {"name": "Overharvesting", "percentage": 68},
            {"name": "Habitat Loss", "percentage": 52},
            {"name": "Water Quality", "percentage": 45},
            {"name": "Climate Change", "percentage": 28},
        ],
        "conservation_actions": [
            {"done": True, "text": "Chesapeake Bay Blue Crab Advisory Report annual monitoring"},
            {"done": True, "text": "Egg-bearing female protection regulations in place"},
            {"done": True, "text": "Commercial harvest quotas established by ASMFC"},
            {"done": False, "text": "Chesapeake Bay nutrient reduction targets not fully met"},
        ],
    },
    "region_assocs": [
        {"region": "Chesapeake Bay", "abundance": "Abundant", "best_season": "May–October"},
        {"region": "Delaware Bay", "abundance": "Common", "best_season": "June–September"},
        {"region": "Sandy Hook Bay", "abundance": "Common", "best_season": "July–September"},
        {"region": "Barnegat Bay", "abundance": "Common", "best_season": "July–September"},
    ],
    "regulations": [
        {"state": "MD", "harvest_legal": True, "min_size_cm": 14.0, "bag_limit": None,
         "season": "April 1 – December 15", "permit_required": "Yes — Commercial license for commercial harvest",
         "authority": "MD Department of Natural Resources"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": 12.7, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — DNREC recreational license",
         "authority": "DNREC Division of Fish & Wildlife"},
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 11.4, "bag_limit": None,
         "season": "Year-round", "permit_required": "No",
         "authority": "NJ Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Striped Bass",
    "scientific_name": "Morone saxatilis",
    "category": "fish",
    "max_length_cm": 180.0,
    "depth_min_m": 0,
    "depth_max_m": 37.0,
    "weight": "Up to 57 kg (125 lbs)",
    "diet": "Carnivore — herring, menhaden, eels, squid, crabs",
    "lifespan": "Up to 30 years",
    "habitat": "Coastal waters, estuaries, rivers (spawning)",
    "migratory": True,
    "about": "The striped bass, known regionally as 'rockfish,' is the most prized game fish of the Mid-Atlantic coast. An anadromous species, it spawns in freshwater rivers but spends most of its life in coastal saltwater. Striped bass populations collapsed in the 1980s from overfishing, triggering one of the first successful federal fishery recovery programs — a story now at risk of repeating as populations decline again.",
    "legal_notice": "Strictly regulated by the Atlantic States Marine Fisheries Commission. Size and bag limits apply in all states. Slot limits (keep fish within a specific size range) are increasingly common.",
    "encounter_tip": "Popular sport fish caught by surf casting, trolling, or jigging. Check current slot limits — some sizes must be released even if legal-sized under old rules.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 55,
        "aware_fact": "Striped bass successfully recovered from near-collapse in the 1980s due to a landmark coast-wide fishing moratorium — but overfishing pressure has caused the stock to decline again since 2012, prompting new emergency measures by ASMFC.",
        "last_assessed": "2023",
        "main_threats": [
            {"name": "Overfishing", "percentage": 74},
            {"name": "Habitat Degradation", "percentage": 48},
            {"name": "Climate Change", "percentage": 40},
            {"name": "Disease (Mycobacteriosis)", "percentage": 35},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC coast-wide management plan in place"},
            {"done": True, "text": "Size and bag limits enforced across all states"},
            {"done": True, "text": "Emergency measures passed in 2023 to reduce harvest"},
            {"done": False, "text": "Stock rebuilding target (2029) not yet achieved"},
        ],
    },
    "region_assocs": [
        {"region": "Chesapeake Bay", "abundance": "Abundant", "best_season": "March–May, October–November", "depth_notes": "Spawning run in spring"},
        {"region": "Delaware Bay", "abundance": "Common", "best_season": "April–June"},
        {"region": "Sandy Hook Bay", "abundance": "Common", "best_season": "May–November"},
        {"region": "NJ Atlantic Shelf", "abundance": "Seasonal", "best_season": "September–December"},
    ],
    "regulations": [
        {"state": "MD", "harvest_legal": True, "min_size_cm": 46.0, "bag_limit": 1,
         "season": "Jan 1 – Dec 31 (slot limits apply)", "permit_required": "Yes — Chesapeake Bay Sport Fishing License",
         "authority": "MD Department of Natural Resources"},
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 71.0, "bag_limit": 1,
         "season": "Jan 1 – Dec 31 (seasonal closures)", "permit_required": "Yes — NJ Saltwater Recreational Registry",
         "authority": "ASMFC / NJ Division of Fish & Wildlife"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": 46.0, "bag_limit": 1,
         "season": "Year-round", "permit_required": "Yes — DNREC recreational license",
         "authority": "DNREC / ASMFC"},
    ],
})

add_creature({
    "common_name": "Horseshoe Crab",
    "scientific_name": "Limulus polyphemus",
    "category": "shellfish",
    "max_length_cm": 61.0,
    "depth_min_m": 0,
    "depth_max_m": 30.0,
    "weight": "Up to 4.5 kg (10 lbs)",
    "diet": "Worms, mollusks, thin-shelled bivalves, algae",
    "lifespan": "20–40 years",
    "habitat": "Sandy and muddy seafloors, estuaries, coastal bays",
    "migratory": True,
    "about": "Horseshoe crabs are not true crabs but are more closely related to spiders and scorpions. They are living fossils — essentially unchanged for 450 million years, predating the dinosaurs by 200 million years. Each spring, hundreds of thousands migrate to Mid-Atlantic beaches to spawn, and their eggs are a critical food source for migratory shorebirds. Their blue copper-based blood is also harvested by the biomedical industry for endotoxin testing of vaccines.",
    "legal_notice": "Harvest is strictly regulated due to ecological importance. Horseshoe crabs are a keystone species for migratory shorebirds, especially the red knot (federally listed as Threatened). Harvest varies by state from prohibited to permit-required.",
    "encounter_tip": "If you find a horseshoe crab flipped on its back on the beach, gently flip it right-side up by the sides of its shell — never by the tail. Do not remove them from the water or beach unnecessarily.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 48,
        "aware_fact": "A single horseshoe crab's blood can be worth up to $60,000 per quart in the biomedical industry. The FDA mandates that every injectable drug and medical device be tested using Limulus Amebocyte Lysate (LAL), a compound found only in horseshoe crab blood.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Biomedical Harvesting", "percentage": 62},
            {"name": "Beach Development", "percentage": 55},
            {"name": "Overharvesting (bait)", "percentage": 48},
            {"name": "Climate Change", "percentage": 30},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC Interstate Fishery Management Plan for Horseshoe Crab"},
            {"done": True, "text": "New Jersey harvest moratorium since 2008"},
            {"done": True, "text": "Delaware Bay spawning beach protections"},
            {"done": False, "text": "Synthetic LAL alternative not yet widely adopted by industry"},
        ],
    },
    "region_assocs": [
        {"region": "Delaware Bay", "abundance": "Abundant (spawning)", "best_season": "May–June (full/new moon)", "depth_notes": "Beach spawning at high tide"},
        {"region": "Rehoboth Beach Shelf", "abundance": "Common", "best_season": "May–August"},
        {"region": "Sandy Hook Bay", "abundance": "Common", "best_season": "May–June"},
    ],
    "regulations": [
        {"state": "DE", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "May 15 – June 15 (spawning closure)", "permit_required": "Yes — DNREC commercial permit",
         "authority": "DNREC Division of Fish & Wildlife"},
        {"state": "NJ", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NJ Division of Fish & Wildlife"},
        {"state": "MD", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "Limited quota system", "permit_required": "Yes — MD DNR commercial permit",
         "authority": "MD Department of Natural Resources"},
    ],
})

add_creature({
    "common_name": "Sand Tiger Shark",
    "scientific_name": "Carcharias taurus",
    "category": "shark",
    "max_length_cm": 320.0,
    "depth_min_m": 0,
    "depth_max_m": 191.0,
    "weight": "Up to 159 kg (350 lbs)",
    "diet": "Carnivore — fish, rays, squid, crustaceans",
    "lifespan": "15–40 years",
    "habitat": "Coastal waters, sandy beaches, rocky reefs, bays",
    "migratory": True,
    "about": "Despite their menacing appearance — with rows of jagged, exposed teeth — sand tiger sharks are docile and slow-moving, rarely posing a threat to humans unless provoked. They are the only shark known to gulp air to maintain neutral buoyancy. Critically endangered on the US East Coast, sand tiger sharks have one of the lowest reproductive rates of any shark: females give birth to just 1–2 pups every two years. Recovery is extremely slow.",
    "legal_notice": "Fully protected in US federal waters. No take or possession permitted. Any accidental capture must be released immediately with minimal handling. Document and report to NOAA HMS.",
    "encounter_tip": "Sand tiger sharks are often seen hovering motionless near the seafloor or in shallow water near piers. They look intimidating but are non-aggressive. If encountered while diving, maintain a calm demeanor and avoid cornering the animal.",
    "conservation": {
        "iucn_level": "Critically Endangered",
        "population_trend": "Decreasing",
        "threat_score": 88,
        "aware_fact": "Sand tiger sharks were once commonly seen along New Jersey beaches. By the early 2000s, bycatch and targeted fishing had reduced their US Atlantic population by an estimated 75%. With females producing only 1–2 pups every two years, it would take decades to recover even if all fishing pressure stopped today.",
        "last_assessed": "2023",
        "main_threats": [
            {"name": "Bycatch", "percentage": 85},
            {"name": "Historical Targeted Fishing", "percentage": 70},
            {"name": "Slow Reproduction", "percentage": 65},
            {"name": "Habitat Degradation", "percentage": 38},
        ],
        "conservation_actions": [
            {"done": True, "text": "Protected under NOAA in all US Atlantic federal waters"},
            {"done": True, "text": "Immediate release required for all incidental catches"},
            {"done": True, "text": "Critical habitat research ongoing"},
            {"done": False, "text": "International protection framework — not fully established"},
            {"done": False, "text": "Stock assessment goal of 1,000 mature adults not reached"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Rare", "best_season": "July–September"},
        {"region": "Rehoboth Beach Shelf", "abundance": "Rare", "best_season": "July–September"},
        {"region": "Ocean City Atlantic Coast", "abundance": "Rare", "best_season": "August–October"},
    ],
    "regulations": [
        {"state": "US", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA Fisheries / HMS Management Division"},
        {"state": "NJ", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA / NJ Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Weakfish",
    "scientific_name": "Cynoscion regalis",
    "category": "fish",
    "max_length_cm": 90.0,
    "depth_min_m": 0,
    "depth_max_m": 55.0,
    "weight": "Up to 8.5 kg (19 lbs)",
    "diet": "Carnivore — shrimp, crabs, small fish, squid",
    "lifespan": "8–17 years",
    "habitat": "Estuaries, coastal bays, nearshore ocean",
    "migratory": True,
    "about": "The weakfish gets its name not from lack of fighting spirit, but from its delicate mouth tissue — hooks tear out easily, making it a challenging catch for anglers. Once extraordinarily abundant along the Mid-Atlantic coast, weakfish populations collapsed dramatically in the 1990s and have never fully recovered. They are considered a sentinel species for estuary health.",
    "legal_notice": "Regulated by ASMFC under a coast-wide management plan. Size and bag limits apply. Recreational and commercial harvest allowed with appropriate licensing.",
    "encounter_tip": "Best caught at dusk or dawn in estuaries with soft bottom. Use light tackle to account for their tender mouth. Popular bait includes shrimp, bucktail jigs, and soft plastic lures.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 50,
        "aware_fact": "Weakfish were once so plentiful they were called 'the poor man's fish' of the Chesapeake. A combination of overfishing, disease, and predation by recovering striped bass populations contributed to a 99% decline in some year-classes during the 1990s–2000s.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Overfishing", "percentage": 65},
            {"name": "Striped Bass Predation", "percentage": 50},
            {"name": "Parasite Disease", "percentage": 42},
            {"name": "Habitat Loss", "percentage": 30},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC coast-wide management plan in effect"},
            {"done": True, "text": "Reduced commercial quotas"},
            {"done": False, "text": "Stock rebuilding target not yet met"},
            {"done": False, "text": "Disease research program underfunded"},
        ],
    },
    "region_assocs": [
        {"region": "Delaware Bay", "abundance": "Uncommon", "best_season": "May–October"},
        {"region": "Chesapeake Bay", "abundance": "Uncommon", "best_season": "May–September"},
        {"region": "Barnegat Bay", "abundance": "Uncommon", "best_season": "June–September"},
    ],
    "regulations": [
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 30.5, "bag_limit": 6,
         "season": "Year-round", "permit_required": "Yes — NJ Saltwater Recreational Registry",
         "authority": "NJ Division of Fish & Wildlife / ASMFC"},
        {"state": "MD", "harvest_legal": True, "min_size_cm": 30.5, "bag_limit": 6,
         "season": "Year-round", "permit_required": "Yes — MD Sport Fishing License",
         "authority": "MD Department of Natural Resources"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": 30.5, "bag_limit": 6,
         "season": "Year-round", "permit_required": "Yes — DNREC license",
         "authority": "DNREC Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Summer Flounder",
    "scientific_name": "Paralichthys dentatus",
    "category": "fish",
    "max_length_cm": 94.0,
    "depth_min_m": 0,
    "depth_max_m": 130.0,
    "weight": "Up to 12.3 kg (27 lbs)",
    "diet": "Carnivore — fish, squid, shrimp, crabs",
    "lifespan": "Up to 20 years",
    "habitat": "Sandy and muddy bottoms, estuaries, coastal bays",
    "migratory": True,
    "about": "The summer flounder — known to anglers as 'fluke' — is a master of camouflage. Both eyes migrate to the left side of its body as a juvenile, allowing it to lie flat on the seafloor and change its skin pattern to match virtually any substrate. It is an ambush predator that strikes with surprising speed. One of the most popular recreational target fish on the Mid-Atlantic coast.",
    "legal_notice": "Regulated under the Summer Flounder, Scup, and Black Sea Bass Fishery Management Plan. Size and bag limits apply and vary by state.",
    "encounter_tip": "Fish on sandy bottoms in 3–20 feet of water with squid strips, Gulp! baits, or bucktail jigs. Keep your bait moving slightly — flounder prefer a slow-moving presentation.",
    "conservation": {
        "iucn_level": "Near Threatened",
        "population_trend": "Stable",
        "threat_score": 32,
        "aware_fact": "Summer flounder underwent a dramatic population recovery after stock collapse in the early 1990s, becoming a model for successful fishery management. However, climate change is shifting their range northward, creating management challenges across state boundaries.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Overfishing", "percentage": 45},
            {"name": "Climate Shift (Range Change)", "percentage": 40},
            {"name": "Habitat Loss", "percentage": 30},
            {"name": "Bycatch", "percentage": 22},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC/MAFMC joint management plan in place"},
            {"done": True, "text": "Annual stock assessment guides quota setting"},
            {"done": True, "text": "Size limits protect spawning-age fish"},
            {"done": False, "text": "Climate-adaptive management framework not yet formalized"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Abundant", "best_season": "May–September"},
        {"region": "Delaware Bay", "abundance": "Common", "best_season": "May–August"},
        {"region": "Ocean City Atlantic Coast", "abundance": "Common", "best_season": "June–September"},
        {"region": "Sandy Hook Bay", "abundance": "Common", "best_season": "June–August"},
    ],
    "regulations": [
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 43.2, "bag_limit": 10,
         "season": "May 1 – Oct 7", "permit_required": "Yes — NJ Saltwater Recreational Registry",
         "authority": "NJ Division of Fish & Wildlife / ASMFC"},
        {"state": "MD", "harvest_legal": True, "min_size_cm": 43.2, "bag_limit": 10,
         "season": "May 1 – Sep 30", "permit_required": "Yes — MD Sport Fishing License",
         "authority": "MD Department of Natural Resources"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": 43.2, "bag_limit": 10,
         "season": "May 1 – Sep 30", "permit_required": "Yes — DNREC license",
         "authority": "DNREC Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Atlantic Menhaden",
    "scientific_name": "Brevoortia tyrannus",
    "category": "fish",
    "max_length_cm": 38.0,
    "depth_min_m": 0,
    "depth_max_m": 20.0,
    "weight": "Up to 0.6 kg (1.3 lbs)",
    "diet": "Filter feeder — phytoplankton, zooplankton",
    "lifespan": "Up to 10 years",
    "habitat": "Coastal bays, estuaries, nearshore ocean",
    "migratory": True,
    "about": "Atlantic menhaden are often called 'the most important fish in the sea' — not because of their value to humans, but because of their role in the ecosystem. They are the primary prey of striped bass, bluefish, osprey, dolphins, and dozens of other species. As filter feeders, they also clean estuarine water at an extraordinary rate. The Chesapeake Bay's largest industrial fishery by volume targets menhaden for fish oil and fishmeal.",
    "legal_notice": "Commercial harvest is permitted under ASMFC quota management. No recreational bag limit — menhaden may be harvested as bait. Reduction fishery (for fish oil/meal) is subject to strict federal quotas.",
    "encounter_tip": "Menhaden are easy to spot — look for large schools near the surface that cause a boiling appearance on the water. They can be caught with cast nets. Excellent live bait for striped bass and bluefish.",
    "conservation": {
        "iucn_level": "Least Concern",
        "population_trend": "Increasing",
        "threat_score": 12,
        "aware_fact": "A single adult menhaden can filter up to 7 gallons of water per minute, making large schools a critical water quality engine for estuaries like the Chesapeake Bay. Their decline correlates directly with increases in harmful algal blooms.",
        "last_assessed": "2021",
        "main_threats": [
            {"name": "Industrial Reduction Fishing", "percentage": 55},
            {"name": "Ecological Cascade (predator recovery)", "percentage": 30},
            {"name": "Habitat Degradation", "percentage": 20},
            {"name": "Climate Change", "percentage": 18},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC catch cap for reduction fishery (Omega Protein)"},
            {"done": True, "text": "Bay-specific harvest limits to protect Chesapeake Bay"},
            {"done": True, "text": "Stock biomass currently above target level"},
            {"done": False, "text": "Ecosystem-based management approach not yet fully implemented"},
        ],
    },
    "region_assocs": [
        {"region": "Chesapeake Bay", "abundance": "Abundant", "best_season": "April–November"},
        {"region": "NJ Atlantic Shelf", "abundance": "Abundant", "best_season": "May–October"},
        {"region": "Ocean City Atlantic Coast", "abundance": "Common", "best_season": "May–October"},
        {"region": "Delaware Bay", "abundance": "Common", "best_season": "May–September"},
    ],
    "regulations": [
        {"state": "MD", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — Commercial permit for reduction fishery",
         "authority": "MD Department of Natural Resources / ASMFC"},
        {"state": "NJ", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "Year-round", "permit_required": "No for recreational bait use",
         "authority": "ASMFC / NJ Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Bluefish",
    "scientific_name": "Pomatomus saltatrix",
    "category": "fish",
    "max_length_cm": 120.0,
    "depth_min_m": 0,
    "depth_max_m": 200.0,
    "weight": "Up to 14.4 kg (31.7 lbs)",
    "diet": "Carnivore — fish, squid, shrimp, crabs — highly aggressive",
    "lifespan": "Up to 9 years",
    "habitat": "Coastal open water, bays, nearshore ocean",
    "migratory": True,
    "about": "Bluefish are among the most aggressive predators in coastal Atlantic waters. They hunt in packs, slashing through schools of baitfish with their razor-sharp teeth in a chaotic feeding frenzy. They continue feeding even when full — a behavior called 'slashing' — biting fish in half and leaving the remains. This ferociousness makes them popular sport fish but also contributes to their reputation as a nuisance when they destroy fishing gear.",
    "legal_notice": "Regulated under the Bluefish Fishery Management Plan (ASMFC). Recreational bag limits apply. No size limit federally, but some states impose minimum sizes.",
    "encounter_tip": "Use a wire leader — bluefish will bite through monofilament line. Spoons, poppers, and cut bait all work well. Be careful handling them: their teeth are extremely sharp and they bite reflexively, even when out of the water.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 45,
        "aware_fact": "Bluefish were so abundant in the 19th century that they disrupted entire local fisheries, reportedly wiping out schools of weakfish and mackerel along the New England coast. Today their population is less than 20% of historic highs.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Overfishing", "percentage": 60},
            {"name": "Forage Fish Decline", "percentage": 52},
            {"name": "Climate Change", "percentage": 38},
            {"name": "Habitat Degradation", "percentage": 25},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC Bluefish FMP annual quota management"},
            {"done": True, "text": "Recreational bag limit of 3 fish/day in effect (2023)"},
            {"done": False, "text": "Stock rebuilding target (2024) at risk of missing"},
            {"done": False, "text": "Ecosystem-based menhaden bait management not coordinated"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Common", "best_season": "May–November"},
        {"region": "Ocean City Atlantic Coast", "abundance": "Common", "best_season": "June–October"},
        {"region": "Rehoboth Beach Shelf", "abundance": "Common", "best_season": "June–October"},
    ],
    "regulations": [
        {"state": "NJ", "harvest_legal": True, "min_size_cm": None, "bag_limit": 3,
         "season": "Year-round", "permit_required": "Yes — NJ Saltwater Recreational Registry",
         "authority": "NJ Division of Fish & Wildlife / ASMFC"},
        {"state": "MD", "harvest_legal": True, "min_size_cm": None, "bag_limit": 3,
         "season": "Year-round", "permit_required": "Yes — MD Sport Fishing License",
         "authority": "MD Department of Natural Resources"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": None, "bag_limit": 3,
         "season": "Year-round", "permit_required": "Yes — DNREC license",
         "authority": "DNREC Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Spiny Dogfish",
    "scientific_name": "Squalus acanthias",
    "category": "shark",
    "max_length_cm": 160.0,
    "depth_min_m": 0,
    "depth_max_m": 900.0,
    "weight": "Up to 9.1 kg (20 lbs)",
    "diet": "Carnivore — fish, squid, crabs, shrimp",
    "lifespan": "Up to 70+ years",
    "habitat": "Coastal and open ocean, cold to temperate waters",
    "migratory": True,
    "about": "The spiny dogfish is one of the most abundant shark species on Earth, yet it is also one of the most vulnerable to overfishing due to its extremely slow maturity and reproduction. Females don't reproduce until age 10–12 and have a gestation period of nearly two years — the longest of any vertebrate. They travel in large, highly organized schools segregated by sex and age. The spines at the base of each dorsal fin deliver a mild venom.",
    "legal_notice": "Commercial harvest permitted under federal quota. Recreational harvest is allowed with no minimum size in most states. Spines should be handled carefully — they can cause painful wounds.",
    "encounter_tip": "Frequently encountered by anglers targeting other species, particularly in cold months. Though considered a nuisance by some, spiny dogfish are a crucial part of the food web. Handle carefully near the dorsal spines.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 52,
        "aware_fact": "A female spiny dogfish pregnant today may have been conceived during the Reagan administration — their gestation period is 22–24 months. This makes population recovery extraordinarily slow: if heavily fished, a cohort lost today won't be replaced for a generation.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Overfishing", "percentage": 70},
            {"name": "Slow Reproduction Rate", "percentage": 65},
            {"name": "Bycatch", "percentage": 48},
            {"name": "Climate Change", "percentage": 32},
        ],
        "conservation_actions": [
            {"done": True, "text": "NOAA annual stock assessment and quota management"},
            {"done": True, "text": "Federal commercial catch limits in place"},
            {"done": False, "text": "International coordination with EU fisheries incomplete"},
            {"done": False, "text": "Rebuilding plan target not on track"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Common", "best_season": "October–April"},
        {"region": "Rehoboth Beach Shelf", "abundance": "Common", "best_season": "October–March"},
    ],
    "regulations": [
        {"state": "NJ", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — NJ Saltwater Recreational Registry",
         "authority": "NOAA / NJ Division of Fish & Wildlife"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": None, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — DNREC license",
         "authority": "NOAA / DNREC"},
    ],
})

add_creature({
    "common_name": "Atlantic Sturgeon",
    "scientific_name": "Acipenser oxyrinchus",
    "category": "fish",
    "max_length_cm": 427.0,
    "depth_min_m": 0,
    "depth_max_m": 50.0,
    "weight": "Up to 363 kg (800 lbs)",
    "diet": "Bottom feeder — worms, mollusks, crustaceans, small fish",
    "lifespan": "Up to 60 years",
    "habitat": "Large coastal rivers (spawning); continental shelf (feeding)",
    "migratory": True,
    "about": "The Atlantic sturgeon is a prehistoric giant — a living fossil whose lineage extends 120 million years. Covered in rows of bony plates called scutes, it once was so abundant in the Hudson River that it was called 'Albany Beef.' Commercial harvesting for their valuable caviar and flesh collapsed populations by the early 1900s. Now federally listed as Endangered, the greatest ongoing threats are vessel strikes and incidental capture in commercial gear.",
    "legal_notice": "Fully protected under the Endangered Species Act. Zero harvest, take, or possession permitted. If accidentally caught, immediately release with minimal handling. Report injuries or mortality to NOAA.",
    "encounter_tip": "Atlantic sturgeon are sometimes spotted jumping clear of the water — a behavior called 'breaching' whose purpose remains unknown. If you see one, keep your distance — vessel strikes are a leading cause of mortality.",
    "conservation": {
        "iucn_level": "Endangered",
        "population_trend": "Stable",
        "threat_score": 68,
        "aware_fact": "Atlantic sturgeon in the New York Bight (Hudson River population) were reduced to near zero by the 1990s. The species has been listed under the ESA since 2012, and genetic research has revealed distinct breeding populations — meaning losing one river population is truly irreplaceable.",
        "last_assessed": "2023",
        "main_threats": [
            {"name": "Vessel Strikes", "percentage": 72},
            {"name": "Commercial Bycatch", "percentage": 65},
            {"name": "Habitat Loss (spawning rivers)", "percentage": 50},
            {"name": "Historical Overfishing", "percentage": 40},
        ],
        "conservation_actions": [
            {"done": True, "text": "Listed as Endangered under the Endangered Species Act (2012)"},
            {"done": True, "text": "NOAA critical habitat designated in major East Coast rivers"},
            {"done": True, "text": "Vessel speed rules in effect in some NY/NJ areas"},
            {"done": False, "text": "Statewide bycatch reduction device requirements not yet universal"},
        ],
    },
    "region_assocs": [
        {"region": "Chesapeake Bay", "abundance": "Rare", "best_season": "March–May (spawning migration)"},
        {"region": "Delaware Bay", "abundance": "Rare", "best_season": "March–May (spawning migration)"},
    ],
    "regulations": [
        {"state": "US", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA Fisheries — Endangered Species Act"},
        {"state": "NJ", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA / NJ Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "Eastern Oyster",
    "scientific_name": "Crassostrea virginica",
    "category": "shellfish",
    "max_length_cm": 25.0,
    "depth_min_m": 0,
    "depth_max_m": 12.0,
    "weight": "Varies widely",
    "diet": "Filter feeder — phytoplankton, detritus",
    "lifespan": "20+ years",
    "habitat": "Subtidal and intertidal oyster reefs, estuaries",
    "migratory": False,
    "about": "The eastern oyster is the reef-builder of the Mid-Atlantic estuary system. A single oyster can filter up to 50 gallons of water per day, making large oyster reefs a critical water quality service in turbid estuaries. Chesapeake Bay oyster populations have declined by over 99% from historic levels due to over-harvesting, disease (MSX and Dermo), and sedimentation from land-use changes. Oyster reef restoration is now a major ecological priority.",
    "legal_notice": "Harvest regulated by individual states. Shellfish sanitation closures apply in areas with poor water quality — always check for open/closed designations before harvest.",
    "encounter_tip": "Wild oyster harvest requires checking local shellfish sanitation maps first. Many areas are closed due to water quality. When harvesting legally, use a proper oyster knife and heavy gloves — the shells are razor-sharp.",
    "conservation": {
        "iucn_level": "Least Concern",
        "population_trend": "Increasing",
        "threat_score": 10,
        "aware_fact": "Historic Chesapeake Bay oyster reefs were so massive they could be seen on nautical charts and posed a navigational hazard to ships. Today, less than 1% of that reef habitat remains. Restoration programs have seeded over 20 billion oyster spat since 2009 with measurable water quality improvements.",
        "last_assessed": "2020",
        "main_threats": [
            {"name": "Disease (MSX/Dermo)", "percentage": 65},
            {"name": "Historical Overharvesting", "percentage": 60},
            {"name": "Sedimentation & Turbidity", "percentage": 55},
            {"name": "Ocean Acidification", "percentage": 40},
        ],
        "conservation_actions": [
            {"done": True, "text": "Maryland Oyster Restoration Initiative — 10 sanctuary reefs"},
            {"done": True, "text": "Billions of oyster spat seeded annually in Chesapeake Bay"},
            {"done": True, "text": "Aquaculture expansion supporting wild stock recovery"},
            {"done": False, "text": "Disease-resistant strain deployment at scale not achieved"},
        ],
    },
    "region_assocs": [
        {"region": "Chesapeake Bay", "abundance": "Recovering", "best_season": "October–March (harvest)", "depth_notes": "Reef habitat concentrated in tributaries"},
        {"region": "Delaware Bay", "abundance": "Common", "best_season": "October–March (harvest)"},
        {"region": "Sandy Hook Bay", "abundance": "Uncommon", "best_season": "September–April"},
    ],
    "regulations": [
        {"state": "MD", "harvest_legal": True, "min_size_cm": 7.6, "bag_limit": None,
         "season": "Oct 1 – Mar 31", "permit_required": "Yes — MD tidal fish license",
         "authority": "MD Department of Natural Resources"},
        {"state": "DE", "harvest_legal": True, "min_size_cm": 7.6, "bag_limit": None,
         "season": "Oct 1 – May 31", "permit_required": "Yes — DNREC shellfish license",
         "authority": "DNREC Division of Fish & Wildlife"},
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 7.6, "bag_limit": None,
         "season": "Sept 1 – May 15", "permit_required": "Yes — NJ Shellfish license",
         "authority": "NJ Division of Fish & Wildlife / DEP"},
    ],
})

add_creature({
    "common_name": "Great White Shark",
    "scientific_name": "Carcharodon carcharias",
    "category": "shark",
    "max_length_cm": 610.0,
    "depth_min_m": 0,
    "depth_max_m": 1200.0,
    "weight": "680–1,100 kg",
    "diet": "Carnivore — seals, sea lions, fish, rays, dolphins",
    "lifespan": "70+ years",
    "habitat": "Coastal and open ocean, worldwide",
    "migratory": True,
    "about": "The great white shark is the world's largest predatory fish and an apex predator in virtually every ocean ecosystem. Despite their fearsome reputation — reinforced by decades of popular culture — great white sharks are responsible for fewer than 10 fatal attacks per year globally. They are vital regulators of marine food webs. Population declines have been severe and they are now classified as Vulnerable by the IUCN, with only an estimated 3,500 adults remaining worldwide.",
    "legal_notice": "Fully protected in US federal waters under the Magnuson-Stevens Act. Harvesting, possessing, or selling is strictly prohibited. Penalties up to $100,000 per violation.",
    "encounter_tip": "Remain calm. Do not thrash or splash. Slowly back toward shore or your vessel. Maintain eye contact. Great white shark attacks on humans are extremely rare — most are investigatory bites. Do not enter the water near marine mammal haul-outs or areas with known feeding activity.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 62,
        "aware_fact": "Only an estimated 3,500 adult great white sharks remain in the world's oceans. Despite being protected in many jurisdictions, they continue to be killed in fishing bycatch, shark culling programs, and the illegal fin trade.",
        "last_assessed": "2021",
        "main_threats": [
            {"name": "Overfishing / Bycatch", "percentage": 72},
            {"name": "Habitat Loss", "percentage": 45},
            {"name": "Climate Change", "percentage": 38},
            {"name": "Ship Strikes", "percentage": 22},
        ],
        "conservation_actions": [
            {"done": True, "text": "Protected under Magnuson-Stevens Act (US)"},
            {"done": True, "text": "CITES Appendix II — international trade regulated"},
            {"done": False, "text": "Global fishing quotas — not yet established"},
            {"done": True, "text": "Shark fin bans in 14 US states"},
        ],
    },
    "region_assocs": [],
    "regulations": [
        {"state": "US", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA Fisheries / Magnuson-Stevens Act"},
    ],
})

add_creature({
    "common_name": "Whale Shark",
    "scientific_name": "Rhincodon typus",
    "category": "shark",
    "max_length_cm": 1220.0,
    "depth_min_m": 0,
    "depth_max_m": 1800.0,
    "weight": "Up to 21,500 kg (47,000 lbs)",
    "diet": "Filter feeder — plankton, krill, fish eggs, small fish",
    "lifespan": "70–150 years (estimated)",
    "habitat": "Open ocean, tropical and warm temperate seas",
    "migratory": True,
    "about": "The whale shark is the largest fish on Earth — and among the most peaceful. Despite their enormous size, they are filter feeders, swimming slowly with their mouths agape to strain plankton, krill, and small fish from the water. They are highly sought by ecotourism operators and represent a key conservation success story where live, swimming sharks are worth far more economically than dead ones. Their populations have nonetheless declined by over 50% in the last 75 years.",
    "legal_notice": "Fully protected globally under CITES Appendix II. No take, possession, purchase, or sale permitted in US waters.",
    "encounter_tip": "Whale sharks are commonly encountered by divers and snorkelers in tropical waters. Maintain at least 3 meters distance and never touch or ride them. Do not use motorized vehicles near feeding whale sharks.",
    "conservation": {
        "iucn_level": "Endangered",
        "population_trend": "Decreasing",
        "threat_score": 71,
        "aware_fact": "A whale shark's spot pattern is as unique as a human fingerprint. Scientists use a platform called Wildbook for Whale Sharks to crowd-source photo ID data, with over 12,000 individual sharks identified from citizen science photos worldwide.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Vessel Strikes", "percentage": 68},
            {"name": "Fishing Bycatch", "percentage": 58},
            {"name": "Illegal Fin Trade", "percentage": 50},
            {"name": "Climate Change / Prey Loss", "percentage": 40},
        ],
        "conservation_actions": [
            {"done": True, "text": "CITES Appendix II — international trade regulated"},
            {"done": True, "text": "Protected in US, Australia, Philippines, and other key habitats"},
            {"done": False, "text": "Global fishing interaction monitoring program not established"},
            {"done": False, "text": "Vessel speed regulations in key habitats not in place"},
        ],
    },
    "region_assocs": [],
    "regulations": [
        {"state": "US", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA Fisheries / CITES Appendix II"},
    ],
})

add_creature({
    "common_name": "Giant Manta Ray",
    "scientific_name": "Mobula birostris",
    "category": "ray",
    "max_length_cm": 700.0,
    "depth_min_m": 0,
    "depth_max_m": 1000.0,
    "weight": "Up to 3,000 kg (6,600 lbs)",
    "diet": "Filter feeder — zooplankton, fish larvae, krill",
    "lifespan": "40+ years",
    "habitat": "Open ocean, coral reefs, coastal waters, cleaning stations",
    "migratory": True,
    "about": "The giant manta ray is the world's largest ray, with a wingspan that can exceed 7 meters. Despite their size, they are filter feeders who pose no threat to humans. They are highly intelligent — among the few animals to pass the mirror self-recognition test — and have the largest brain-to-body ratio of any fish. Mantas visit 'cleaning stations' on coral reefs where smaller fish remove parasites from their skin. They are now critically threatened by targeted gill plate fishing.",
    "legal_notice": "Fully protected in US waters under the MMPA (Marine Mammal Protection Act equivalent via ESA listing). No take or harassment permitted.",
    "encounter_tip": "If you encounter a manta ray while diving, hold still and let it approach you — they are curious animals. Do not grab their cephalic fins (horn-like lobes near the mouth) or touch the skin, as this disrupts their protective mucus layer.",
    "conservation": {
        "iucn_level": "Endangered",
        "population_trend": "Decreasing",
        "threat_score": 69,
        "aware_fact": "Manta ray gill plates are sold in Chinese traditional medicine markets for up to $500 per kg, despite no scientific evidence of medicinal benefit. A single manta ray generates an estimated $1 million in ecotourism revenue over its lifetime versus ~$500 as a one-time catch.",
        "last_assessed": "2022",
        "main_threats": [
            {"name": "Targeted Gill Plate Fishing", "percentage": 80},
            {"name": "Bycatch", "percentage": 60},
            {"name": "Vessel Strikes", "percentage": 42},
            {"name": "Climate Change / Prey Loss", "percentage": 35},
        ],
        "conservation_actions": [
            {"done": True, "text": "CITES Appendix II listing — international trade regulated"},
            {"done": True, "text": "Protected in US, Australia, Ecuador, and Maldives waters"},
            {"done": False, "text": "Comprehensive global trade ban — not yet achieved"},
            {"done": False, "text": "High-seas bycatch monitoring program not established"},
        ],
    },
    "region_assocs": [],
    "regulations": [
        {"state": "US", "harvest_legal": False, "min_size_cm": None, "bag_limit": 0,
         "season": "N/A", "permit_required": "N/A",
         "authority": "NOAA Fisheries / ESA / CITES Appendix II"},
    ],
})

add_creature({
    "common_name": "Atlantic Bluefin Tuna",
    "scientific_name": "Thunnus thynnus",
    "category": "fish",
    "max_length_cm": 300.0,
    "depth_min_m": 0,
    "depth_max_m": 1000.0,
    "weight": "Up to 680 kg (1,500 lbs)",
    "diet": "Carnivore — herring, mackerel, squid, eels",
    "lifespan": "Up to 40 years",
    "habitat": "Open ocean, coastal waters during feeding migrations",
    "migratory": True,
    "about": "The Atlantic bluefin tuna is the apex of pelagic evolution — warm-blooded, capable of swimming over 70 mph, and able to dive to depths of 1,000 meters. A single large specimen can be worth over $1 million at Japanese fish markets, where it is the most prized sashimi fish in the world. This extraordinary value has driven it to the edge of commercial extinction, with populations declining over 70% from the 1970s to early 2000s before partial recovery under ICCAT management.",
    "legal_notice": "Strictly regulated by ICCAT (International Commission for the Conservation of Atlantic Tunas). Commercial harvest requires HMS Angling permit. Recreational anglers must possess a Highly Migratory Species permit. Strict reporting requirements.",
    "encounter_tip": "Bluefin tuna are found following baitfish schools in late summer and fall. Look for diving gannets and other seabirds as a surface indicator. Use large diving plugs, mackerel-rigged wire line, or chunking with butterfish.",
    "conservation": {
        "iucn_level": "Endangered",
        "population_trend": "Stable",
        "threat_score": 65,
        "aware_fact": "A single Atlantic bluefin tuna sold at Tokyo's Toyosu Market on New Year's Day 2019 fetched $3.1 million USD — over $6,700 per pound. This extraordinary price illustrates both the cultural value of the fish and the financial pressure driving overfishing.",
        "last_assessed": "2021",
        "main_threats": [
            {"name": "International Overfishing", "percentage": 78},
            {"name": "ICCAT Quota Non-Compliance", "percentage": 60},
            {"name": "Warming Ocean (Prey Shifts)", "percentage": 45},
            {"name": "Bycatch", "percentage": 38},
        ],
        "conservation_actions": [
            {"done": True, "text": "ICCAT harvest quotas for Western and Eastern stocks"},
            {"done": True, "text": "US HMS Highly Migratory Species permit required"},
            {"done": True, "text": "Western Atlantic stock at ~50% of 1975 biomass (partial recovery)"},
            {"done": False, "text": "ICCAT quota compliance — chronic violations by some nations"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Seasonal", "best_season": "August–November"},
        {"region": "Ocean City Atlantic Coast", "abundance": "Seasonal", "best_season": "September–November"},
    ],
    "regulations": [
        {"state": "US", "harvest_legal": True, "min_size_cm": 182.0, "bag_limit": 3,
         "season": "June 1 – Nov 20 (varies by category)", "permit_required": "Yes — NOAA HMS Angling Permit",
         "authority": "NOAA Fisheries / ICCAT"},
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 182.0, "bag_limit": 3,
         "season": "June 1 – Nov 20", "permit_required": "Yes — Federal HMS permit + NJ Saltwater Registry",
         "authority": "NOAA / NJ Division of Fish & Wildlife"},
    ],
})

add_creature({
    "common_name": "American Lobster",
    "scientific_name": "Homarus americanus",
    "category": "shellfish",
    "max_length_cm": 64.0,
    "depth_min_m": 0,
    "depth_max_m": 480.0,
    "weight": "Up to 20 kg (44 lbs)",
    "diet": "Omnivore — fish, mollusks, worms, plant material",
    "lifespan": "Over 100 years (estimated)",
    "habitat": "Rocky seafloors, kelp beds, sandy/muddy bottoms",
    "migratory": False,
    "about": "The American lobster is the most commercially valuable marine invertebrate in North America, generating over $1 billion annually for the fishing industry. They can live over 100 years and continue growing indefinitely — the largest specimens ever caught weighed over 20 kg. Climate change is driving a dramatic northward range shift, with warming Gulf of Maine temperatures collapsing populations in southern New England while benefiting the Maine fishery.",
    "legal_notice": "Harvest regulated under the American Lobster Fishery Management Plan (ASMFC). Minimum and maximum size gauges are required. V-notching of egg-bearing females is required in some states. Trap permits required.",
    "encounter_tip": "Lobster can be caught in wire traps baited with fresh herring or fish frames. Check regulations for minimum carapace length (measured from back of eye socket to rear of carapace). All egg-bearing females must be released.",
    "conservation": {
        "iucn_level": "Vulnerable",
        "population_trend": "Decreasing",
        "threat_score": 43,
        "aware_fact": "American lobsters in southern New England (New York, Connecticut, Rhode Island) have declined catastrophically — over 80% since 1997 — due to warming waters that increase disease susceptibility and disrupt molting cycles. Meanwhile, Maine lobster catches hit record highs as the species moves north. The entire US lobster fishery may shift to Canadian waters within decades.",
        "last_assessed": "2023",
        "main_threats": [
            {"name": "Climate Change (Warming Gulf of Maine)", "percentage": 72},
            {"name": "Shell Disease (Epizootic)", "percentage": 60},
            {"name": "Overharvesting in southern range", "percentage": 45},
            {"name": "Habitat Loss", "percentage": 30},
        ],
        "conservation_actions": [
            {"done": True, "text": "ASMFC mandatory minimum carapace length gauges"},
            {"done": True, "text": "V-notching egg-bearing females required in most states"},
            {"done": True, "text": "Maximum size gauge protects large broodstock"},
            {"done": False, "text": "Climate-adaptive stock assessment framework not established"},
        ],
    },
    "region_assocs": [
        {"region": "NJ Atlantic Shelf", "abundance": "Uncommon", "best_season": "October–April", "depth_notes": "Deep offshore movement in summer"},
        {"region": "Rehoboth Beach Shelf", "abundance": "Uncommon", "best_season": "October–March"},
    ],
    "regulations": [
        {"state": "NJ", "harvest_legal": True, "min_size_cm": 8.3, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — NJ commercial lobster permit or recreational license",
         "authority": "ASMFC / NJ Division of Fish & Wildlife"},
        {"state": "US", "harvest_legal": True, "min_size_cm": 8.3, "bag_limit": None,
         "season": "Year-round", "permit_required": "Yes — Federal lobster trap permit",
         "authority": "NOAA Fisheries / ASMFC"},
    ],
})

db.commit()
db.close()
print("Database seeded successfully.")
