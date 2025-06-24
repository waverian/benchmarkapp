git checkout main
git checkout benchmark_basic
git reset --soft HEAD^1
git stash
git merge main
git stash apply
git commit -m "Benchmark_Basic:"
