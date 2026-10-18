"""
=============================================================
VERSET DU JOUR — Église Smyrne
=============================================================
Sélection quotidienne de versets bibliques inspirants,
avec formatage optimisé pour le partage WhatsApp et réseaux sociaux.
"""

from datetime import date

VERSETS = [
    {
        "texte": "Je puis tout par celui qui me fortifie.",
        "reference": "Philippiens 4:13",
        "theme": "Force & Foi"
    },
    {
        "texte": "L'Éternel est mon berger : je ne manquerai de rien.",
        "reference": "Psaume 23:1",
        "theme": "Protection"
    },
    {
        "texte": "Car je connais les projets que j'ai formés sur vous, dit l'Éternel, projets de paix et non de malheur, afin de vous donner un avenir et de l'espérance.",
        "reference": "Jérémie 29:11",
        "theme": "Espérance"
    },
    {
        "texte": "Confie-toi en l'Éternel de tout ton cœur, et ne t'appuie pas sur ta sagesse ; reconnais-le dans toutes tes voies, et il aplanira tes sentiers.",
        "reference": "Proverbes 3:5-6",
        "theme": "Confiance"
    },
    {
        "texte": "Ne crains rien, car je suis avec toi ; ne promène pas des regards inquiets, car je suis ton Dieu ; je te fortifie, je viens à ton secours, je te soutiens de ma droite triomphante.",
        "reference": "Ésaïe 41:10",
        "theme": "Courage"
    },
    {
        "texte": "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.",
        "reference": "Jean 3:16",
        "theme": "Amour de Dieu"
    },
    {
        "texte": "Mais ceux qui se confient en l'Éternel renouvellent leur force. Ils prennent le vol comme les aigles ; ils courent, et ne se lassent point ; ils marchent, et ne se fatiguent point.",
        "reference": "Ésaïe 40:31",
        "theme": "Renouvellement"
    },
    {
        "texte": "Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos.",
        "reference": "Matthieu 11:28",
        "theme": "Paix & Repos"
    },
    {
        "texte": "L'Éternel est ma lumière et mon salut : de qui aurais-je crainte ? L'Éternel est le soutien de ma vie : de qui aurais-je peur ?",
        "reference": "Psaume 27:1",
        "theme": "Victoire"
    },
    {
        "texte": "La paix que je vous laisse, c'est ma paix que je vous donne. Je ne vous la donne pas comme le monde donne. Que votre cœur ne se trouble point, et ne s'alarme point.",
        "reference": "Jean 14:27",
        "theme": "Sérénité"
    },
    {
        "texte": "Si Dieu est pour nous, qui sera contre nous ?",
        "reference": "Romains 8:31",
        "theme": "Assurance"
    },
    {
        "texte": "Recommande ton sort à l'Éternel, mets en lui ta confiance, et il agira.",
        "reference": "Psaume 37:5",
        "theme": "Foi"
    },
    {
        "texte": "Toutes choses concourent au bien de ceux qui aiment Dieu, de ceux qui sont appelés selon son dessein.",
        "reference": "Romains 8:28",
        "theme": "Providence"
    },
    {
        "texte": "La prière fervente du juste a une grande efficace.",
        "reference": "Jacques 5:16",
        "theme": "Prière"
    },
    {
        "texte": "Soyez toujours joyeux. Priez sans cesse. Rendez grâces en toutes choses, car c'est à votre égard la volonté de Dieu en Jésus-Christ.",
        "reference": "1 Thessaloniciens 5:16-18",
        "theme": "Reconnaissance"
    },
]


def get_verset_du_jour():
    """Retourne le verset du jour calculé de façon déterministe selon la date."""
    aujourdhui = date.today()
    index = aujourdhui.timetuple().tm_yday % len(VERSETS)
    verset = VERSETS[index].copy()
    verset["date"] = aujourdhui.strftime("%d/%m/%Y")
    
    # Texte préformaté pour le partage WhatsApp
    verset["whatsapp_share_text"] = (
        f"📖 *Verset du Jour — Église Smyrne (5e CELPA)*\n\n"
        f"« {verset['texte']} »\n\n"
        f"— *{verset['reference']}*\n\n"
        f"🕊️ Que la paix du Seigneur vous accompagne aujourd'hui !"
    )
    return verset
