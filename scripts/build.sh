source config.sh

# Download and build
wget https://github.com/${GITHUB_USER}/${GITHUB_REPO}/archive/master.zip
unzip master.zip
rm master.zip
FOLDER=${GITHUB_REPO}-master
python render.py --assets_dir ${FOLDER}/assets --templates_dir ../templates --out_dir ../
rm -R ${FOLDER}

# Commit
git add ../index.html
git commit -m "$(date)"
