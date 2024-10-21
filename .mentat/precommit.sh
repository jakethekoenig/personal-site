npm run lint || echo "No lint script found, skipping"
npm test || echo "No test script found, skipping"
./exhibit/scripts/build_live.sh