import galah

galah.galah_config(email="luke@ando.id.au")

data = galah.atlas_species(rank="genus", filters="year>=2025")

print(data["Family"].tolist())
