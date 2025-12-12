import streamlit as st

# --- Ağaç profilleri (ideal değer + tolerans) ---
tree_profiles = {
    "zeytin": {
        "salinity": {"ideal": 4, "tol": 1},
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

# Varsayılan ağırlıklar
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

# --- Hesaplama fonksiyonu ---
def recommend_tree(soil):
    s = {
        "salinity": clamp(float(soil["salinity"]), 0, 20),
        "moisture": clamp(float(soil["moisture"]), 0, 100),
        "pH": clamp(float(soil["pH"]), 3.0, 10.0),
        "soil_type": soil["soil_type"].lower(),
        "organic": clamp(float(soil["organic"]), 0, 100),
        "slope": clamp(float(soil["slope"]), 0, 100),
    }

    w = normalize_weights(default_weights)
    tree_scores = {}

    for tree, prof in tree_profiles.items():
        score = (
            continuous_score(s["salinity"], prof["salinity"]["ideal"], prof["salinity"]["tol"]) * w["salinity"] +
            continuous_score(s["moisture"], prof["moisture"]["ideal"], prof["moisture"]["tol"]) * w["moisture"] +
            continuous_score(s["pH"], prof["pH"]["ideal"], prof["pH"]["tol"]) * w["pH"] +
            continuous_score(s["organic"], prof["organic"]["ideal"], prof["organic"]["tol"]) * w["organic"] +
            continuous_score(s["slope"], prof["slope"]["ideal"], prof["slope"]["tol"]) * w["slope"] +
            prof["soil_type_scores"].get(s["soil_type"], 0.5) * w["soil_type"]
        )

        tree_scores[tree] = round(score * 100, 2)

    return sorted(tree_scores.items(), key=lambda x: x[1], reverse=True)

# --- Streamlit Arayüzü ---
st.title("🌱 Ağaç Öneri Sistemi")

salinity = st.number_input("Tuzluluk (dS/m)", 0.0, 20.0, 2.0)
moisture = st.number_input("Nem (%)", 0.0, 100.0, 25.0)
pH = st.number_input("pH", 3.0, 10.0, 7.0)
organic = st.number_input("Organik Madde (%)", 0.0, 100.0, 2.0)
slope = st.number_input("Eğim (%)", 0.0, 100.0, 5.0)
soil_type = st.selectbox("Toprak Tipi", ["kumlu", "tınlı", "killi"])

if st.button("Ağacı Öner"):
    soil = {
        "salinity": salinity,
        "moisture": moisture,
        "pH": pH,
        "organic": organic,
        "slope": slope,
        "soil_type": soil_type
    }

    ranked = recommend_tree(soil)

    st.subheader("Skorlar:")
    for name, score in ranked:
        st.write(f"**{name.capitalize()} → {score}%**")

    st.success(f"🌿 Önerilen Ağaç: **{ranked[0][0].upper()}**")
