from vector_store import store_day, find_similar_days

store_day(999, "sergio_test", "2026-01-01", "This is a test entry for checking Chroma storage.")

results = find_similar_days("sergio_test", "This is a test entry for checking Chroma storage.", n_results=1)
print(results)