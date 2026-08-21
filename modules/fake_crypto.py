import os
import sys
import hashlib
import secrets
import string
import json
import time

try:
    import kevbin
    from kevbin import box_table, box, txt, num, head, sub, prompt, cprint, color
except ImportError:
    class _C:
        def __getattr__(self, _): return lambda *a, **kw: None
    kevbin = _C()
    def box_table(*a, **kw): pass
    def box(*a, **kw): pass
    def txt(*a): return str(a)
    def num(*a): return str(a)
    def head(*a): return str(a)
    def sub(*a): return str(a)
    def prompt(msg=''):
        if msg:
            print(msg, end='', flush=True)
        return input()
    def cprint(*a, **kw): print(*[x for x in a if isinstance(x, str)])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    try:
        kevbin.pause()
    except:
        input("\n\033[90mPress Enter to continue...\033[0m")


WORDS_2048 = [
    "abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse",
    "access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act",
    "action","actor","actress","actual","adapt","add","addict","address","adjust","admit",
    "adult","advance","advice","aerobic","affair","afford","afraid","again","age","agent",
    "agree","ahead","aim","air","airport","aisle","alarm","album","alcohol","alert",
    "alien","all","alley","allow","almost","alone","alpha","already","also","alter",
    "always","amateur","amazing","among","amount","amused","analyst","anchor","ancient","anger",
    "angle","angry","animal","ankle","announce","annual","another","answer","antenna","antique",
    "anxiety","any","apart","apology","appear","apple","approve","april","arch","arctic",
    "area","arena","argue","arm","armed","armor","army","around","arrange","arrest",
    "arrive","arrow","art","artefact","artist","artwork","ask","aspect","assault","asset",
    "assist","assume","asthma","athlete","atom","attack","attend","attitude","attract","auction",
    "audit","august","aunt","author","auto","autumn","average","avocado","avoid","awake",
    "aware","awesome","awful","awkward","axis","baby","bachelor","bacon","badge","bag",
    "balance","balcony","ball","bamboo","banana","banner","bar","barely","bargain","barrel",
    "base","basic","basket","battle","beach","bean","beauty","because","become","beef",
    "before","begin","behave","behind","believe","below","belt","bench","benefit","best",
    "betray","better","between","beyond","bicycle","bid","bike","bind","biology","bird",
    "birth","bitter","black","blade","blame","blanket","blast","bleak","bless","blind",
    "blood","blossom","blow","blue","blur","blush","board","boat","body","boil",
    "bomb","bone","bonus","book","boost","border","boring","borrow","boss","bottom",
    "bounce","box","boy","bracket","brain","brand","brass","brave","bread","breeze",
    "brick","bridge","brief","bright","bring","brisk","broccoli","broken","bronze","broom",
    "brother","brown","brush","bubble","buddy","budget","buffalo","build","bulb","bulk",
    "bullet","bundle","bunny","burden","burger","burst","bus","business","busy","butter",
    "buyer","buzz","cabbage","cabin","cable","cactus","cage","cake","call","calm",
    "camera","camp","can","canal","cancel","candy","cannon","canoe","canvas","canyon",
    "capable","capital","captain","car","carbon","card","cargo","carpet","carry","cart",
    "case","cash","casino","castle","casual","cat","catalog","catch","category","cattle",
    "caught","cause","caution","cave","ceiling","celery","cement","census","century","cereal",
    "certain","chair","chalk","champion","change","chaos","chapter","charge","chase","cheap",
    "check","cheese","chef","cherry","chest","chicken","chief","child","chimney","choice",
    "choose","chronic","chuckle","chunk","churn","citizen","city","civil","claim","clap",
    "clarify","claw","clay","clean","clerk","clever","cliff","climb","clinic","clip",
    "clock","clog","close","cloth","cloud","clown","club","clump","cluster","clutch",
    "coach","coast","coconut","code","coffee","coil","coin","collect","color","column",
    "combine","come","comfort","comic","common","company","concert","conduct","confirm","congress",
    "connect","consider","control","convince","cook","cool","copper","copy","coral","core",
    "corn","correct","cost","cotton","couch","country","couple","course","cousin","cover",
    "coyote","crack","cradle","craft","cram","crane","crash","crater","crawl","crazy",
    "cream","credit","creek","crew","cricket","crime","crisp","critic","crop","cross",
    "crouch","crowd","crucial","cruel","cruise","crumble","crush","cry","crystal","cube",
    "culture","cup","cupboard","curious","current","curtain","curve","cushion","custom","cute",
    "cycle","dad","damage","damp","dance","danger","daring","dash","daughter","dawn",
    "day","deal","debate","debris","decade","december","decide","decline","decorate","decrease",
    "deer","defense","define","defy","degree","delay","deliver","demand","demise","denial",
    "dentist","deny","depart","depend","deposit","depth","deputy","derive","describe","desert",
    "design","desk","despair","destroy","detail","detect","develop","device","devote","diagram",
    "dial","diamond","diary","dice","diesel","diet","differ","digital","dignity","dilemma",
    "dinner","dinosaur","direct","dirt","disagree","discover","disease","dish","dismiss","display",
    "distance","divert","divide","divorce","dizzy","doctor","document","dog","doll","dolphin",
    "domain","donate","donkey","donor","door","dose","double","dove","draft","dragon",
    "drama","drastic","draw","dream","dress","drift","drill","drink","drip","drive",
    "drop","drum","dry","duck","dumb","dune","during","dust","dutch","duty",
    "dwarf","dynamic","eager","eagle","early","earn","earth","easily","east","easy",
    "echo","ecology","economy","edge","edit","educate","effort","egg","eight","either",
    "elbow","elder","electric","elegant","element","elephant","elevator","elite","else","embark",
    "embody","embrace","emerge","emotion","employ","empower","empty","enable","encourage","end",
    "endless","endorse","enemy","energy","enforce","engage","engine","enhance","enjoy","enlist",
    "enough","enrich","enroll","ensure","enter","entire","entry","envelope","episode","equal",
    "equip","era","erase","erode","erosion","error","erupt","escape","essay","essence",
    "estate","eternal","ethics","evidence","evil","evoke","evolve","exact","example","excess",
    "exchange","excite","exclude","excuse","execute","exercise","exhaust","exhibit","exile","exist",
    "exit","exotic","expand","expect","expire","explain","expose","express","extend","extra",
    "eye","eyebrow","fabric","face","faculty","fade","faint","faith","fall","false",
    "fame","family","famous","fan","fancy","fantasy","farm","fashion","fat","fatal",
    "father","fatigue","fault","favorite","feature","february","federal","fee","feed","feel",
    "female","fence","festival","fetch","fever","few","fiber","fiction","field","figure",
    "file","film","filter","final","find","fine","finger","finish","fire","firm",
    "fiscal","fish","fit","fitness","fix","flag","flame","flash","flat","flavor",
    "flee","flight","flip","float","flock","floor","flower","fluid","flush","fly",
    "foam","focus","fog","foil","fold","follow","food","foot","force","forest",
    "forget","fork","fortune","forum","forward","fossil","foster","found","fox","fragile",
    "frame","frequent","fresh","friend","fringe","frog","front","frost","frown","frozen",
    "fruit","fuel","fun","funny","furnace","fury","future","gadget","gain","galaxy",
    "gallery","game","gap","garage","garbage","garden","garlic","garment","gas","gasp",
    "gate","gather","gauge","gaze","general","genius","genre","gentle","genuine","gesture",
    "ghost","giant","gift","giggle","ginger","giraffe","girl","give","glad","glance",
    "glare","glass","glide","glimpse","globe","gloom","glory","glove","glow","glue",
    "goat","goddess","gold","golden","goose","gorilla","gospel","gossip","govern","gown",
    "grab","grace","grain","grant","grape","grass","gravity","great","green","grid",
    "grief","grit","grocery","group","grow","grunt","guard","guess","guide","guilt",
    "guitar","gun","gym","habit","hair","half","hammer","hamster","hand","happy",
    "harbor","hard","harsh","harvest","hat","have","hawk","hazard","head","health",
    "heart","heavy","hedgehog","height","hello","helmet","help","hen","hero","hip",
    "hire","history","hobby","hockey","hold","hole","holiday","hollow","home","honey",
    "hood","hope","horn","horror","horse","hospital","host","hotel","hour","hover",
    "hub","huge","human","humble","humor","hundred","hungry","hunt","hurdle","hurry",
    "hurt","husband","hybrid","ice","icon","idea","identify","idle","ignore","ill",
    "illegal","illness","image","imitate","immense","immune","impact","impose","improve","impulse",
    "inch","include","income","increase","index","indicate","indoor","industry","infant","inflict",
    "inform","initial","inject","inmate","inner","innocent","input","inquiry","insane","insect",
    "inside","inspire","install","intact","interest","into","invest","invite","involve","iron",
    "island","isolate","issue","item","ivory","jacket","jaguar","jar","jazz","jealous",
    "jeans","jelly","jewel","job","join","joke","journey","joy","judge","juice",
    "jump","jungle","junior","junk","just","kangaroo","keen","keep","ketchup","key",
    "kick","kid","kidney","kind","kingdom","kiss","kit","kitchen","kite","kitten",
    "kiwi","knee","knife","knock","know","lab","label","labor","ladder","lady",
    "lake","lamp","language","laptop","large","later","latin","laugh","laundry","lava",
    "law","lawn","lawsuit","layer","lazy","leader","leaf","learn","leave","lecture",
    "left","leg","legal","legend","leisure","lemon","lend","length","lens","leopard",
    "lesson","letter","level","liberty","library","license","life","lift","light","like",
    "limb","limit","link","lion","liquid","list","little","live","lizard","load",
    "loan","lobster","local","lock","logic","lonely","long","loop","lottery","loud",
    "lounge","love","loyal","lucky","luggage","lumber","lunar","lunch","luxury","lyrics",
    "machine","mad","magic","magnet","maid","mail","main","major","make","mammal",
    "man","manage","mandate","mango","mansion","manual","maple","marble","march","margin",
    "marine","market","marriage","mask","mass","master","match","material","math","matrix",
    "matter","maximum","maze","meadow","mean","measure","meat","mechanic","medal","media",
    "melody","melt","member","memory","mention","menu","mercy","merge","merit","merry",
    "mesh","message","metal","method","middle","midnight","milk","million","mimic","mind",
    "minimum","minor","minute","miracle","mirror","misery","miss","mistake","mix","mixed",
    "mixture","mobile","model","modify","mom","moment","monitor","monkey","monster","month",
    "moon","moral","more","morning","mosquito","mother","motion","motor","mountain","mouse",
    "move","movie","much","muffin","mule","multiply","muscle","museum","mushroom","music",
    "must","mutual","myself","mystery","myth","naive","name","napkin","narrow","nasty",
    "nation","nature","near","neck","need","negative","neglect","neither","nephew","nerve",
    "nest","net","network","neutral","never","news","next","nice","night","noble",
    "noise","nominee","noodle","normal","north","nose","notable","nothing","notice","novel",
    "now","nuclear","number","nurse","nut","oak","obey","object","oblige","obscure",
    "observe","obtain","obvious","occur","ocean","october","odor","off","offer","office",
    "often","oil","okay","old","olive","olympic","omit","once","one","onion",
    "online","only","open","opera","opinion","oppose","option","orange","orbit","orchard",
    "order","ordinary","organ","orient","original","orphan","ostrich","other","outdoor","outer",
    "output","outside","oval","oven","over","own","owner","oxygen","oyster","ozone",
    "pact","paddle","page","pair","palace","palm","panda","panel","panic","panther",
    "paper","parade","parent","park","parrot","party","pass","patch","path","patient",
    "patrol","pattern","pause","pave","payment","peace","peanut","pear","peasant","pelican",
    "pen","penalty","pencil","people","pepper","perfect","permit","person","pet","phone",
    "photo","phrase","physical","piano","picnic","picture","piece","pig","pigeon","pill",
    "pilot","pink","pioneer","pipe","pistol","pitch","pizza","place","planet","plastic",
    "plate","play","please","pledge","pluck","plug","plunge","poem","poet","point",
    "polar","pole","police","pond","pony","pool","popular","portion","position","possible",
    "post","potato","pottery","poverty","powder","power","practice","praise","predict","prefer",
    "prepare","present","pretty","prevent","price","pride","primary","print","priority","prison",
    "private","prize","problem","process","produce","profit","program","project","promote","proof",
    "property","prosper","protect","proud","provide","public","pudding","pull","pulp","pulse",
    "pumpkin","punch","pupil","puppy","purchase","purity","purpose","purse","push","put",
    "puzzle","pyramid","quality","quantum","quarter","question","quick","quit","quiz","quote",
    "rabbit","raccoon","race","rack","radar","radio","rage","rail","rain","raise",
    "rally","ramp","ranch","random","range","rapid","rare","rate","rather","raven",
    "raw","razor","ready","real","reason","rebel","rebuild","recall","receive","recipe",
    "record","recycle","reduce","reflect","reform","region","regret","regular","reject","relax",
    "release","relief","rely","remain","remember","remind","remove","render","renew","rent",
    "reopen","repair","repeat","replace","report","require","rescue","resemble","resist","resource",
    "response","result","retire","retreat","return","reunion","reveal","review","reward","rhythm",
    "rib","ribbon","rice","rich","ride","ridge","rifle","right","rigid","ring",
    "riot","ripple","risk","ritual","rival","river","road","roast","robot","robust",
    "rocket","romance","roof","rookie","room","rose","rotate","rough","round","route",
    "royal","rubber","rude","rug","rule","run","runway","rural","sad","saddle",
    "sadness","safe","sail","salad","salmon","salon","salt","salute","same","sample",
    "sand","satisfy","satoshi","sauce","sausage","save","say","scale","scan","scare",
    "scatter","scene","scheme","school","science","scissors","scorpion","scout","scrap","screen",
    "script","scrub","sea","search","season","seat","second","secret","section","security",
    "seed","seek","segment","select","sell","seminar","senior","sense","sentence","series",
    "service","session","settle","setup","seven","shadow","shaft","shallow","share","shed",
    "shell","sheriff","shield","shift","shine","ship","shiver","shock","shoe","shoot",
    "shop","short","shoulder","shove","shrimp","shrug","shuffle","shy","sibling","sick",
    "side","siege","sight","sign","silent","silk","silly","silver","similar","simple",
    "since","sing","siren","sister","situate","six","size","skate","sketch","ski",
    "skill","skin","skirt","skull","slab","slam","sleep","slender","slide","slight",
    "slim","slogan","slot","slow","slush","small","smart","smile","smoke","smooth",
    "snack","snake","snap","sniff","snow","soap","soccer","social","sock","soda",
    "soft","solar","soldier","solid","solution","solve","someone","song","soon","sorry",
    "sort","soul","sound","soup","source","south","space","spare","speak","special",
    "speed","spell","spend","sphere","spice","spider","spike","spin","spirit","split",
    "sponsor","spoon","sport","spot","spray","spread","spring","spy","square","squeeze",
    "squirrel","stable","stadium","staff","stage","stairs","stamp","stand","start","state",
    "stay","steak","steel","stem","step","stereo","stick","still","sting","stock",
    "stomach","stone","stool","story","stove","strategy","street","strike","strong","struggle",
    "student","stuff","stumble","style","subject","submit","subway","success","such","sudden",
    "suffer","sugar","suggest","suit","summer","sun","sunny","sunset","super","supply",
    "supreme","sure","surface","surge","surprise","surround","survey","suspect","sustain","swallow",
    "swamp","swap","swarm","swear","sweet","swim","swing","switch","sword","symbol",
    "symptom","syrup","system","table","tackle","tag","tail","talent","talk","tank",
    "tape","target","task","taste","tattoo","taxi","teach","team","tell","ten",
    "tenant","tennis","tent","term","test","text","thank","that","theme","then",
    "theory","there","they","thing","this","thought","three","thrive","throw","thumb",
    "thunder","ticket","tide","tiger","tilt","timber","time","tiny","tip","tired",
    "tissue","title","toast","tobacco","today","toddler","toe","together","toilet","token",
    "tomato","tomorrow","tone","tongue","tonight","tool","tooth","top","topic","topple",
    "torch","tornado","tortoise","toss","total","tourist","toward","tower","town","toy",
    "track","trade","traffic","tragic","train","transfer","trap","trash","travel","tray",
    "treat","tree","trend","trial","tribe","trick","trigger","trim","trip","trophy",
    "trouble","truck","true","truly","trumpet","trust","truth","try","tube","tuna",
    "tunnel","turkey","turn","turtle","twelve","twenty","twice","twin","twist","two",
    "type","typical","ugly","umbrella","unable","unaware","uncle","uncover","under","undo",
    "unfair","unfold","unhappy","uniform","union","unique","unit","universe","unknown","unlock",
    "until","unusual","unveil","update","upgrade","uphold","upon","upper","upset","urban",
    "usage","use","used","useful","useless","usual","utility","vacant","vacuum","vague",
    "valid","valley","valve","van","vanish","vapor","various","vast","vault","vehicle",
    "velvet","vendor","venture","venue","verb","verify","version","very","vessel","veteran",
    "viable","vibrant","vicious","victory","video","view","village","vintage","violin","virtual",
    "virus","visa","visit","visual","vital","vivid","vocal","voice","void","volcano",
    "volume","vote","voyage","wage","wagon","wait","walk","wall","walnut","want",
    "warfare","warm","warrior","wash","wasp","waste","water","wave","way","wealth",
    "weapon","wear","weasel","weather","web","wedding","weekend","weird","welcome","well",
    "west","wet","whale","what","wheat","wheel","when","where","whip","whisper",
    "wide","width","wife","wild","will","win","window","wine","wing","wink",
    "winner","winter","wire","wisdom","wise","wish","witness","wolf","woman","wonder",
    "wood","wool","word","work","world","worry","worth","wrap","wreck","wrestle",
    "wrist","write","wrong","yard","year","yellow","you","young","youth","zebra",
    "zero","zone","zoo"
]

FAKE_WALLETS = {
    "bitcoin": {
        "prefix": "1",
        "name": "Bitcoin (Legacy)",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║              BITCOIN WALLET (LEGACY)                 ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet                                 ║
║  Type:       P2PKH (Legacy)                          ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    },
    "bitcoin_segwit": {
        "prefix": "bc1q",
        "name": "Bitcoin (SegWit)",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║              BITCOIN WALLET (SEGWIT)                 ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet                                 ║
║  Type:       P2WPKH (Bech32)                         ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    },
    "ethereum": {
        "prefix": "0x",
        "name": "Ethereum",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║                ETHEREUM WALLET                       ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet (Chain ID: 1)                   ║
║  Type:       EOA                                     ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    },
    "litecoin": {
        "prefix": "ltc1",
        "name": "Litecoin",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║                LITECOIN WALLET                       ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet                                 ║
║  Type:       P2WPKH (Bech32)                         ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    },
    "dogecoin": {
        "prefix": "D",
        "name": "Dogecoin",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║                DOGECOIN WALLET                       ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet                                 ║
║  Type:       P2PKH                                  ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    },
    "monero": {
        "prefix": "4",
        "name": "Monero",
        "gen": lambda addr, priv: f"""╔══════════════════════════════════════════════════════╗
║                MONERO WALLET                         ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Address:    {addr:<39} ║
║  Private:    {priv[:16]}...{priv[-16:]:<15} ║
║  Network:    Mainnet                                 ║
║  Type:       Stealth (Ring signatures)               ║
║                                                      ║
║  ⚠  THIS IS A SIMULATED WALLET FOR LARP/TESTING     ║
║  ⚠  NOT A REAL WALLET — NO REAL FUNDS EXIST          ║
║                                                      ║
╚══════════════════════════════════════════════════════╝"""
    }
}

WALLET_ADDRESS_CHARS = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def generate_seed_phrase(word_count=12):
    return ' '.join(secrets.choice(WORDS_2048) for _ in range(word_count))

def generate_hex_key(length=64):
    return secrets.token_hex(length // 2)

def generate_fake_address(prefix, length=34):
    addr_chars = WALLET_ADDRESS_CHARS
    body = ''.join(secrets.choice(addr_chars) for _ in range(length - len(prefix)))
    return prefix + body

def generate_fake_private_key():
    return '0x' + secrets.token_hex(32)

def display_seed_grid(seed_words):
    words = seed_words.split()
    print()
    cprint("  ╔══════════════════════════════════════════════════╗", "yellow")
    cprint("  ║            RECOVERY SEED PHRASE                 ║", "yellow")
    cprint("  ╠══════════════════════════════════════════════════╣", "yellow")
    for i in range(0, len(words), 3):
        row = words[i:i+3]
        line = "  ║  "
        for j, w in enumerate(row):
            idx = i + j + 1
            line += f"  {idx:>2}. {w:<14}"
        line += "  ║"
        cprint(line, "yellow")
    cprint("  ╠══════════════════════════════════════════════════╣", "yellow")
    cprint("  ║  ⚠  WRITE THESE DOWN AND STORE SECURELY        ║", "red")
    cprint("  ║  ⚠  SIMULATED — NOT REAL CRYPTO SEEDS           ║", "red")
    cprint("  ╚══════════════════════════════════════════════════╝", "yellow")
    print()

def display_portfolio(balance_usd, holdings, tx_history):
    print()
    cprint("  ╔══════════════════════════════════════════════════════════════════════════════════════╗", "cyan")
    cprint("  ║                          FAKE PORTFOLIO DASHBOARD                                  ║", "cyan")
    cprint("  ╠══════════════════════════════════════════════════════════════════════════════════════╣", "cyan")
    cprint(f"  ║  Total Balance:  ${balance_usd:>14,.2f} USD                                          ║", "green")
    cprint(f"  ║  24h Change:     {secrets.choice(['+','+','+','-','-'])}{random.uniform(0.1,8.5):.2f}%{'':>53}║", "green")
    cprint("  ╠══════════════════════════════════════════════════════════════════════════════════════╣", "cyan")
    cprint("  ║  Coin          Amount           Price (USD)          Value (USD)       24h         ║", "cyan")
    cprint("  ╠══════════════════════════════════════════════════════════════════════════════════════╣", "cyan")
    for coin in holdings:
        chg = secrets.choice(['+','+','+','-','-']) + f"{random.uniform(0.05,12.0):.2f}%"
        val = coin['amount'] * coin['price']
        cprint(f"  ║  {coin['sym']:<6}  {coin['amount']:>14,.8f}   ${coin['price']:>12,.2f}   ${val:>14,.2f}   {chg:>8}  ║", "white")
    cprint("  ╠══════════════════════════════════════════════════════════════════════════════════════╣", "cyan")
    cprint("  ║  Recent Transactions:                                                              ║", "cyan")
    for tx in tx_history[:5]:
        cprint(f"  ║    {tx['type']:>6} {tx['amount']:<12} {tx['coin']} → {tx['addr'][:12]}...  {tx['time']:<14}     ║", "white")
    cprint("  ╠══════════════════════════════════════════════════════════════════════════════════════╣", "cyan")
    cprint("  ║  ⚠  ALL DATA IS SIMULATED — NO REAL FUNDS OR TRANSACTIONS                         ║", "red")
    cprint("  ╚══════════════════════════════════════════════════════════════════════════════════════╝", "cyan")
    print()

import random

def run(self=None):
    while True:
        clear()
        cprint("  ╔══════════════════════════════════════════════════╗", "yellow")
        cprint("  ║           FAKE CRYPTO WALLET GENERATOR          ║", "yellow")
        cprint("  ║            LARP / SIMULATION ONLY                ║", "yellow")
        cprint("  ╠══════════════════════════════════════════════════╣", "yellow")
        cprint("  ║  [1]  Generate Wallet + Seed Phrase              ║", "white")
        cprint("  ║  [2]  Generate Wallet (no seed)                  ║", "white")
        cprint("  ║  [3]  Generate Multiple Wallets                  ║", "white")
        cprint("  ║  [4]  Fake Portfolio Dashboard                   ║", "white")
        cprint("  ║  [5]  Generate Seed Phrase Only                  ║", "white")
        cprint("  ║  [6]  Generate Private Key Only                  ║", "white")
        cprint("  ║  [7]  Bulk Generate (save to file)              ║", "white")
        cprint("  ║  [0]  Back                                       ║", "red")
        cprint("  ╚══════════════════════════════════════════════════╝", "yellow")
        choice = prompt("\033[33m  choice > \033[0m")
        if choice == '0':
            return
        elif choice == '1':
            coins = list(FAKE_WALLETS.keys())
            print()
            for i, c in enumerate(coins, 1):
                cprint(f"    [{i}] {FAKE_WALLETS[c]['name']}", "white")
            idx = prompt("\033[33m  coin > \033[0m")
            try:
                coin = coins[int(idx)-1]
            except:
                coin = "bitcoin"
            wallet = FAKE_WALLETS[coin]
            seed = generate_seed_phrase()
            priv = generate_hex_key(64)
            addr = generate_fake_address(wallet['prefix'])
            clear()
            cprint(f"  Wallet Type: {wallet['name']}", "cyan")
            display_seed_grid(seed)
            print(wallet['gen'](addr, priv))
            pause()
        elif choice == '2':
            coins = list(FAKE_WALLETS.keys())
            print()
            for i, c in enumerate(coins, 1):
                cprint(f"    [{i}] {FAKE_WALLETS[c]['name']}", "white")
            idx = prompt("\033[33m  coin > \033[0m")
            try:
                coin = coins[int(idx)-1]
            except:
                coin = "bitcoin"
            wallet = FAKE_WALLETS[coin]
            priv = generate_hex_key(64)
            addr = generate_fake_address(wallet['prefix'])
            clear()
            print(wallet['gen'](addr, priv))
            cprint(f"\n  Private Key (hex): {priv}", "yellow")
            pause()
        elif choice == '3':
            try:
                count = int(prompt("\033[33m  how many wallets? (1-20) > \033[0m"))
                count = max(1, min(20, count))
            except:
                count = 5
            clear()
            cprint(f"\n  Generating {count} wallets...\n", "cyan")
            for i in range(count):
                coin = secrets.choice(list(FAKE_WALLETS.keys()))
                wallet = FAKE_WALLETS[coin]
                priv = generate_hex_key(64)
                addr = generate_fake_address(wallet['prefix'])
                seed = generate_seed_phrase()
                cprint(f"  --- Wallet {i+1}: {wallet['name']} ---", "green")
                cprint(f"  Address:  {addr}", "white")
                cprint(f"  Private:  {priv[:20]}...{priv[-16:]}", "white")
                cprint(f"  Seed:     {seed[:40]}...", "white")
                print()
            pause()
        elif choice == '4':
            coin_prices = [
                {"sym": "BTC", "name": "Bitcoin", "price": random.uniform(42000, 68000)},
                {"sym": "ETH", "name": "Ethereum", "price": random.uniform(2200, 3800)},
                {"sym": "SOL", "name": "Solana", "price": random.uniform(80, 180)},
                {"sym": "DOGE", "name": "Dogecoin", "price": random.uniform(0.08, 0.35)},
                {"sym": "XMR", "name": "Monero", "price": random.uniform(120, 280)},
                {"sym": "LTC", "name": "Litecoin", "price": random.uniform(60, 120)},
            ]
            holdings = []
            total = 0
            for c in coin_prices:
                amt = random.uniform(0.001, 5.0)
                val = amt * c['price']
                total += val
                holdings.append({"sym": c["sym"], "amount": amt, "price": c["price"]})
            txs = []
            addrs = [generate_fake_address("1") for _ in range(5)]
            for j in range(5):
                txs.append({
                    "type": random.choice(["SEND", "RECV"]),
                    "amount": f"{random.uniform(0.001, 2.0):.6f}",
                    "coin": random.choice(["BTC", "ETH", "SOL"]),
                    "addr": addrs[j],
                    "time": f"{random.randint(0,23)}h ago"
                })
            display_portfolio(total, holdings, txs)
            pause()
        elif choice == '5':
            try:
                wc = int(prompt("\033[33m  word count (12/15/24) > \033[0m"))
                if wc not in (12, 15, 24):
                    wc = 12
            except:
                wc = 12
            seed = generate_seed_phrase(wc)
            clear()
            display_seed_grid(seed)
            pause()
        elif choice == '6':
            priv = generate_hex_key(64)
            clear()
            cprint(f"\n  Private Key (hex):  {priv}", "yellow")
            cprint(f"  Length:             {len(priv)} chars", "white")
            pause()
        elif choice == '7':
            try:
                count = int(prompt("\033[33m  how many? (1-100) > \033[0m"))
                count = max(1, min(100, count))
            except:
                count = 10
            fname = prompt("\033[33m  filename (default: fake_wallets.txt) > \033[0m") or "fake_wallets.txt"
            lines = [f"=== FAKE WALLET BATCH — GENERATED {time.strftime('%Y-%m-%d %H:%M:%S')} ==="]
            lines.append("=== SIMULATED DATA FOR LARP/TESTING ONLY ===\n")
            for i in range(count):
                coin = secrets.choice(list(FAKE_WALLETS.keys()))
                wallet = FAKE_WALLETS[coin]
                addr = generate_fake_address(wallet['prefix'])
                priv = generate_hex_key(64)
                seed = generate_seed_phrase()
                lines.append(f"--- Wallet {i+1}: {wallet['name']} ---")
                lines.append(f"  Address:  {addr}")
                lines.append(f"  Private:  {priv}")
                lines.append(f"  Seed:     {seed}")
                lines.append("")
            with open(fname, 'w') as f:
                f.write('\n'.join(lines))
            clear()
            cprint(f"\n  Saved {count} fake wallets to {fname}", "green")
            pause()
        else:
            cprint("  invalid choice", "red")
            time.sleep(0.5)
