import pandas as pd
import re

# === 1. Chargement ===
df = pd.read_excel("FICHIERS PHARMAS AVEC COLONNES SELECTIONNEES HUBSPOT.xlsx")
prenoms_df = pd.read_csv("Prenoms.csv", sep=";", encoding="latin1")
prenoms_df.columns = ["prenom", "genre", "langue", "frequence"]
set_prenoms = set(prenoms_df["prenom"].str.capitalize())

# === 2. Fonctions de nettoyage générique ===
def clean_text(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    return s.title()

def clean_postal(code):
    if pd.isna(code):
        return None
    c = re.sub(r"\D", "", str(code))
    return c.zfill(5) if len(c) <= 5 else c[:5]

def clean_city(ville):
    return clean_text(ville)

def clean_address(addr):
    if pd.isna(addr):
        return None
    s = str(addr).strip()
    s = re.sub(r"\s+", " ", s)
    m = re.match(r"^(\d+\s*)(.*)$", s)
    if m:
        num, reste = m.groups()
        return f"{num}{reste.title()}"
    return s.title()

# === 3. Extraction civilité / prénom / nom / genre ===
def extract_civility(interlocuteur):
    if pd.isna(interlocuteur):
        return None
    t = interlocuteur.upper()
    if "MME" in t: return "Mme"
    if "M " in t or t.startswith("M."): return "M"
    if "DR" in t: return "Dr"
    return None

def split_nom_prenom(interlocuteur):
    """
    1) Supprime la civilité uniquement si elle est en tête (M, Mme, Dr).
    2) Reconnaît prénoms composés (espaces/tiret) en set_prenoms.
    3) Teste inversion nom↔prénom.
    4) Fallback : dernier mot = prénom, reste = nom.
    """
    if pd.isna(interlocuteur):
        return None, None

    t = interlocuteur.strip()

    # 1) retirer la civilité en début seulement
    #    - M, M., Mme, Dr (avec ou sans point)
    t = re.sub(r'^(M\.?|Mme|Dr)\s+', '', t, flags=re.IGNORECASE)

    # 2) découpe en mots
    words = [w.capitalize() for w in t.split()]
    n = len(words)

    # 3) forward detection (espaces / tiret)
    for i in range(1, n):
        candidat_espace = " ".join(words[:i])
        candidat_tiret  = "-".join(words[:i])
        if candidat_espace in set_prenoms or candidat_tiret in set_prenoms:
            return candidat_espace if candidat_espace in set_prenoms else candidat_tiret, \
                   " ".join(words[i:])

    # 4) inversion detection
    for i in range(1, n):
        candidat_espace = " ".join(words[i:])
        candidat_tiret  = "-".join(words[i:])
        if candidat_espace in set_prenoms or candidat_tiret in set_prenoms:
            return candidat_espace if candidat_espace in set_prenoms else candidat_tiret, \
                   " ".join(words[:i])

    # 5) fallback : dernier mot = prénom, reste = nom
    if n >= 2:
        return words[-1], " ".join(words[:-1])

    # 6) cas d’un seul mot
    return None, words[0]

def infer_gender_from_civ(civ):
    if civ == "M":   return "Homme"
    if civ == "Mme": return "Femme"
    return None

# === 4. Formatage entreprise, téléphones et email ===
def clean_company(name):
    if pd.isna(name):
        return None
    s = name.replace("PHARMACIE", "").strip().title()
    return f"Pharmacie {s}"

def format_phone(phone):
    if pd.isna(phone):
        return None
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("0"):
        return "+33" + digits[1:]
    if digits.startswith("33"):
        return "+" + digits
    return digits

def best_email(row):
    for col in ["Email client", "Mail PMGroup"]:
        v = row.get(col)
        if pd.notna(v) and "@" in v:
            return v.strip().lower()
    return None

# === 5. Application du pipeline de nettoyage ===
df_out = df.copy()

# 5.1 Texte générique
for col in ["Raison sociale", "Pays", "Site internet"]:
    df_out[col] = df_out[col].apply(clean_text)

# 5.2 Adresse & localisation
df_out["Adresse"]     = df_out["Adresse"].apply(clean_address)
df_out["Code postal"] = df_out["Code postal"].apply(clean_postal)
df_out["Ville"]       = df_out["Ville"].apply(clean_city)

# 5.3 Civilité / Prénom / Nom / Genre
df_out["Civilité"] = df_out["Interlocuteur"].apply(extract_civility)
df_out[["Prénom","Nom"]] = df_out["Interlocuteur"].apply(
    lambda x: pd.Series(split_nom_prenom(x))
)
df_out["Genre"] = df_out["Civilité"].apply(infer_gender_from_civ)

# 5.4 Entreprise, téléphones, email
df_out["Entreprise formatée"]   = df_out["Raison sociale"].apply(clean_company)
df_out["Portable formaté"]      = df_out["Portable"].apply(format_phone)
df_out["Téléphone formaté"]     = df_out["Téléphone"].apply(format_phone)
df_out["Téléphone.1 formaté"]   = df_out["Téléphone.1"].apply(format_phone)
df_out["Email principal"]       = df_out.apply(best_email, axis=1)

# 5.5 Contact complet
df_out["Contact complet"] = df_out[
    ["Prénom","Nom","Email principal","Portable formaté"]
].astype(str).agg(" / ".join, axis=1)

# === 6. Debug : vérification de l’utilisation de la base de prénoms ===
print(f"🔍 Prénoms chargés : {len(set_prenoms)}")
print("Exemples dans la base :", list(set_prenoms)[:10])
nb_total = len(df_out)
nb_match = df_out["Prénom"].isin(set_prenoms).sum()
print(f"✅ Prénoms reconnus : {nb_match} / {nb_total} ({nb_match/nb_total:.1%})")
non_rec = df_out.loc[
    ~df_out["Prénom"].isin(set_prenoms),
    ["Interlocuteur","Prénom"]
]
print("⚠️  Quelques prénoms non-reconnus :", non_rec.head(5).to_dict(orient="records"))

# === 7. Détection qualité avec motifs ===
def quality_reasons(row):
    reasons = []
    if pd.isna(row["Prénom"]): reasons.append("Prénom manquant")
    if pd.isna(row["Nom"]): reasons.append("Nom manquant")
    if pd.isna(row["Email principal"]): reasons.append("Email manquant")
    if pd.isna(row["Portable formaté"]) \
    and pd.isna(row["Téléphone formaté"]) \
    and pd.isna(row["Téléphone.1 formaté"]):
        reasons.append("Téléphone manquant")
    if pd.isna(row["Adresse"]):     reasons.append("Adresse manquante")
    if pd.isna(row["Code postal"]): reasons.append("Code postal manquant")
    if pd.isna(row["Ville"]):       reasons.append("Ville manquante")
    return reasons

df_out["Raison_Verif"] = df_out.apply(
    lambda r: "; ".join(quality_reasons(r)), axis=1
)
df_out["Flag_Qualité"] = df_out["Raison_Verif"].apply(
    lambda x: "À vérifier" if x else ""
)

# === 8. Export CSV séparé ===
df_out.to_csv("Contacts_Cleaned.csv", sep=";", encoding="utf-8-sig", index=False)
print("✅ Nettoyage + flag qualité + motifs terminés — output: Contacts_Cleaned.csv")
