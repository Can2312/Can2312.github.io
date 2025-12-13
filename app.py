import streamlit as st

# --- Ağaç profilleri (ideal değer + tolerans) ---
tree_profiles = {
    "zeytin": {
        "salinity": {"ideal": 0, "tol": 5},
        "moisture": {"ideal": 23.5, "tol": 5.5},
        "pH": {"ideal": 7, "tol": 1},
        "organic": {"ideal": 1, "tol": 0.5},
        "slope": {"ideal": 6, "tol": 6},
        "soil_type_scores": {"kumlu": 0.95, "tınlı": 0.95, "killi": 0.4},
    },

    "badem": {
        "salinity": {"ideal": 0.75, "tol": 0.75},
        "moisture": {"ideal": 23, "tol": 5},
        "pH": {"ideal": 7, "tol": 1},
        "organic": {"ideal": 3, "tol": 1},
        "slope": {"ideal": 15, "tol": 10},
        "soil_type_scores": {"kumlu": 0.4, "tınlı": 1.0, "killi": 0.3},
    },

    "ceviz": {
        "salinity": {"ideal": 2, "tol": 2},
        "moisture": {"ideal": 27, "tol": 5},
        "pH": {"ideal": 7, "tol": 0.5},
        "organic": {"ideal": 2.75, "tol": 0.75},
        "slope": {"ideal": 2.5, "tol": 2.5},
        "soil_type_scores": {"kumlu": 0.4, "tınlı": 1.0, "killi": 0.5},
    },

    "nar": {
        "salinity": {"ideal": 2, "tol": 2},
        "moisture": {"ideal": 21.5, "tol": 3.5},
        "pH": {"ideal": 6.25, "tol": 0.75},
        "organic": {"ideal": 3, "tol": 1},
        "slope": {"ideal": 1.5, "tol": 1.5},
        "soil_type_scores": {"kumlu": 0.95, "tınlı": 0.95, "killi": 0.4},
    }
}

# Varsayılan ağırlıklar (%)
default_weights = {
    "pH": 15,
    "slope": 10,
    "moisture": 25,
    "salinity": 20,
    "soil_type": 15,
    "organic": 15
}

# --- Yardımcı fonksiyonlar ---
def normalize_weights(weights):
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}

def clamp(x, a, b):
    return max(a, min(b, x))

def continuous_score(value, ideal, tol):
    diff = abs(value - ideal)
    score = 1 - (diff / tol)
    return clamp(score, 0, 1)

# --- Ana fonksiyon ---
def recommend_tree(soil, weights=None):

    s = {
        "salinity": clamp(float(soil.get("salinity", 0)), 0, 20),
        "moisture": clamp(float(soil.get("moisture", 0)), 0, 100),
        "pH": clamp(float(soil.get("pH", 7.0)), 3.0, 10.0),
        "soil_type": soil.get("soil_type", "tınlı").lower(),
        "organic": clamp(float(soil.get("organic", 3.0)), 0, 100),
        "slope": clamp(float(soil.get("slope", 0)), 0, 100)
    }

    if weights is None:
        weights = default_weights.copy()

    w_norm = normalize_weights(weights)
    tree_scores = {}

    for tree, prof in tree_profiles.items():
        score_salinity = continuous_score(s["salinity"], prof["salinity"]["ideal"], prof["salinity"]["tol"])
        score_moisture = continuous_score(s["moisture"], prof["moisture"]["ideal"], prof["moisture"]["tol"])
        score_pH = continuous_score(s["pH"], prof["pH"]["ideal"], prof["pH"]["tol"])
        score_organic = continuous_score(s["organic"], prof["organic"]["ideal"], prof["organic"]["tol"])
        score_slope = continuous_score(s["slope"], prof["slope"]["ideal"], prof["slope"]["tol"])

        soil_t = s["soil_type"]
        if " " in soil_t:
            parts = soil_t.split()
            score_soil_type = sum(
                prof["soil_type_scores"].get(p, 0.5) for p in parts
            ) / len(parts)
        else:
            score_soil_type = prof["soil_type_scores"].get(soil_t, 0.5)

        total_score = (
            score_salinity * w_norm["salinity"] +
            score_moisture * w_norm["moisture"] +
            score_pH * w_norm["pH"] +
            score_soil_type * w_norm["soil_type"] +
            score_organic * w_norm["organic"] +
            score_slope * w_norm["slope"]
        )

        tree_scores[tree] = round(total_score * 100, 2)

    ranked = sorted(tree_scores.items(), key=lambda x: x[1], reverse=True)

    st.subheader("🌳 Ağaç Skorları")
    for tree, score in ranked:
        st.write(f"**{tree.capitalize()}**: {score}%")

    best = ranked[0][0]
    st.success(f"✅ Önerilen Ağaç: {best.upper()}")

    return ranked

# --------------------------
# STREAMLIT ARAYÜZÜ
# --------------------------

st.title("🌱 Toprak Verisine Göre Ağaç Öneri Sistemi")

soil = {
    "salinity": st.number_input("Tuzluluk (dS/m)", 0.0, 20.0, 0.0),
    "moisture": st.number_input("Sululuk (%)", 0.0, 100.0, 20.0),
    "pH": st.number_input("pH", 3.0, 10.0, 7.0),
    "soil_type": st.selectbox(
        "Toprak tipi",
        ["kumlu", "tınlı", "killi", "kumlu tınlı", "kumlu killi", "tınlı killi"]
    ),
    "organic": st.number_input("Organik madde (%)", 0.01, 100.0, 2.0),
    "slope": st.number_input("Eğim (%)", 0.0, 50.0, 5.0)
}

if st.button("Ağaç Öner"):
    recommend_tree(soil)
