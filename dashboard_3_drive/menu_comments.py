import random
import pandas as pd


WASTE_REDUCTION_TIPS = {
    "general": [
        "Les restes peuvent être transformés en compost pour le jardin de l'école.",
        "Nous avons ajusté les portions pour réduire le gaspillage.",
        "Ce menu a été optimisé pour minimiser les déchets alimentaires.",
        "Les élèves ont été consultés pour ce choix de menu.",
        "Ce menu utilise des ingrédients de saison pour réduire l'empreinte carbone."
    ],
    "entrée": {
        "Taboulé": [
            "Le taboulé est préparé avec les restes de légumes de la veille.",
            "Les restes de taboulé peuvent être utilisés dans une salade composée le lendemain."
        ],
        "Carottes râpées": [
            "Les épluchures de carottes sont utilisées pour faire un bouillon.",
            "Les carottes sont issues de l'agriculture locale pour réduire le transport."
        ],
        "Concombres": [
            "Les concombres trop mûrs sont transformés en soupe froide.",
            "Les épluchures de concombres sont utilisées pour l'eau aromatisée servie au repas."
        ],
        "Betteraves": [
            "Les fanes de betteraves sont utilisées en salade.",
            "Les betteraves sont cuites à la vapeur pour préserver les nutriments."
        ],
        "Salade verte": [
            "Les feuilles extérieures de la salade sont utilisées pour le compost.",
            "La salade est servie sans assaisonnement pour que chacun puisse doser selon son goût."
        ],
        "Pamplemousse": [
            "Les écorces de pamplemousse sont utilisées pour parfumer les desserts.",
            "Les pamplemousses trop acides sont transformés en jus pour le goûter."
        ]
    },
    "plat": {
        "Poulet rôti": [
            "Les carcasses de poulet sont utilisées pour faire un bouillon.",
            "Le poulet non consommé sera utilisé dans une salade le lendemain."
        ],
        "Steak haché": [
            "La viande est issue d'élevages locaux pour réduire l'empreinte carbone.",
            "Les portions ont été ajustées selon l'appétit moyen des enfants."
        ],
        "Lasagnes": [
            "Les lasagnes contiennent des légumes de saison pour réduire le gaspillage.",
            "Les restes de lasagnes peuvent être congelés pour un repas ultérieur."
        ],
        "Rôti de bœuf": [
            "Les chutes de viande sont utilisées pour préparer un hachis le lendemain.",
            "Le bœuf est servi avec une sauce légère pour plaire à plus d'enfants."
        ],
        "Rôti de porc": [
            "Les restes de porc seront utilisés dans des sandwichs pour les sorties scolaires.",
            "Le porc est cuisiné avec des herbes du jardin pédagogique de l'école."
        ],
        "Poisson pané": [
            "Le poisson est issu de pêche durable.",
            "Les portions ont été ajustées pour réduire le gaspillage."
        ]
    },
    "légumes": {
        "Petits pois": [
            "Les petits pois sont servis avec leur jus pour plus de saveur.",
            "Les cosses sont utilisées pour faire un bouillon végétal."
        ],
        "Haricots verts": [
            "Les bouts des haricots sont utilisés pour le compost de l'école.",
            "Les haricots trop mûrs sont mixés en purée."
        ],
        "Riz": [
            "Le riz non consommé sera utilisé pour faire un riz cantonais le lendemain.",
            "Le riz est cuit avec précision pour éviter qu'il ne soit trop sec ou trop humide."
        ],
        "Légumes": [
            "Les légumes sont issus de l'agriculture locale et de saison.",
            "Les épluchures sont utilisées pour faire un bouillon."
        ],
        "Carottes": [
            "Les carottes sont cuites avec leur peau pour préserver les nutriments.",
            "Les fanes de carottes sont utilisées pour faire du pesto."
        ],
        "Frites": [
            "Les pommes de terre sont cuites au four pour réduire la matière grasse.",
            "Les épluchures sont transformées en chips croustillantes."
        ]
    },
    "dessert": {
        "Fruit frais": [
            "Les fruits trop mûrs sont transformés en compote.",
            "Les épluchures de fruits sont utilisées pour faire des infusions."
        ],
        "Compote": [
            "La compote est préparée avec les fruits trop mûrs de la semaine.",
            "Les pots de compote sont réutilisés pour des activités manuelles."
        ],
        "Gâteau": [
            "Le gâteau est préparé avec des ingrédients de saison.",
            "Les restes de gâteau sont proposés au goûter."
        ],
        "Crème dessert": [
            "La crème dessert est servie dans des portions adaptées aux enfants.",
            "Les pots sont recyclés pour des activités créatives."
        ]
    },
    "laitage": {
        "Yaourt nature": [
            "Les yaourts sont servis avec un choix de sucre ou confiture à part.",
            "Les pots de yaourt sont réutilisés pour des semis dans le jardin de l'école."
        ],
        "Fromage blanc": [
            "Le fromage blanc est proposé nature pour que chacun puisse l'assaisonner selon son goût.",
            "Les portions sont adaptées à l'appétit des enfants."
        ],
        "Petit suisse": [
            "Les petits suisses sont proposés avec un choix de sucre ou de confiture.",
            "Les emballages sont collectés pour un projet artistique."
        ],
        "Saint Paulin": [
            "Le fromage est coupé en portions adaptées pour éviter le gaspillage.",
            "Les croûtes non consommées sont utilisées pour parfumer une soupe."
        ],
        "Emmental": [
            "L'emmental est râpé sur place pour plus de fraîcheur.",
            "Les portions sont adaptées à l'appétit des enfants."
        ],
        "Camembert": [
            "Le camembert est servi à température ambiante pour développer ses arômes.",
            "Les portions sont adaptées pour réduire le gaspillage."
        ]
    }
}

def get_menu_comments(menu_item, category):
    """
    Get waste reduction comments for a specific menu item and category.
    
    Args:
        menu_item (str): The name of the menu item
        category (str): The category of the item (entrée, plat, légumes, dessert, laitage)
        
    Returns:
        str: A comment about waste reduction for this item
    """
    # Check if we have specific comments for this item
    if category in WASTE_REDUCTION_TIPS and menu_item in WASTE_REDUCTION_TIPS[category]:
        comments = WASTE_REDUCTION_TIPS[category][menu_item]
    else:
        
        comments = WASTE_REDUCTION_TIPS["general"]
    
    # Return a random comment from the available ones
    return random.choice(comments)

def get_daily_menu_comment(menu_row):
    """
    Generate a comprehensive comment for a daily menu.
    
    Args:
        menu_row (dict): A dictionary containing the menu items for a day
        
    Returns:
        str: A comment about waste reduction for the entire menu
    """
    comments = []
    
    # Add comments for each part of the menu if available
    for category, item_key in [
        ("entrée", "Entrée"), 
        ("plat", "Plat"), 
        ("légumes", "Légumes"), 
        ("dessert", "Dessert"), 
        ("laitage", "Laitage")
    ]:
        if item_key in menu_row and pd.notna(menu_row[item_key]):
            item = menu_row[item_key]
            comments.append(get_menu_comment(item, category))
    
    # If we have at least one specific comment, return it
    if comments:
        return random.choice(comments)
    
    # Otherwise return a general comment
    return random.choice(WASTE_REDUCTION_TIPS["general"])

def get_menu_comment(item, category):
    """
    Get a comment for a specific menu item.
    
    Args:
        item (str): The name of the menu item
        category (str): The category of the item
        
    Returns:
        str: A formatted comment string
    """
    if category in WASTE_REDUCTION_TIPS and item in WASTE_REDUCTION_TIPS[category]:
        comment = random.choice(WASTE_REDUCTION_TIPS[category][item])
    else:
        # Use general comments if no specific ones are available
        comment = random.choice(WASTE_REDUCTION_TIPS["general"])
    
    return f"{item}: {comment}"

def get_weekly_waste_tip():
    """
    Get a general tip about reducing food waste for the week.
    
    Returns:
        str: A general waste reduction tip
    """
    weekly_tips = [
        "Cette semaine, nous avons réduit le gaspillage alimentaire de 15% grâce à vos suggestions !",
        "Savez-vous que les restes de la cantine sont compostés pour le jardin de l'école ?",
        "Cette semaine, nous utilisons principalement des produits locaux pour réduire notre empreinte carbone.",
        "Nous avons ajusté les portions en fonction des retours des élèves pour réduire le gaspillage.",
        "Les menus de cette semaine ont été élaborés pour minimiser les déchets alimentaires.",
        "Participez à notre défi 'zéro déchet' cette semaine en finissant votre assiette !",
        "Les légumes servis cette semaine proviennent du potager pédagogique de l'école."
    ]
    return random.choice(weekly_tips)