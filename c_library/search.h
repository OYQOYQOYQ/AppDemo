#ifndef SEARCH_H
#define SEARCH_H

// 搜索结果结构体
typedef struct {
    int* indices;
    int count;
    int capacity;
} SearchResult;

// 搜索算法接口函数声明
SearchResult* init_search_result();
void add_to_result(SearchResult* result, int index);
void free_search_result(SearchResult* result);
SearchResult* linear_search(const char** items, int items_count, const char* keyword);
int binary_search(const char** sorted_items, int items_count, const char* keyword);
int levenshtein_distance(const char* s1, const char* s2);
SearchResult* fuzzy_search(const char** items, int items_count, const char* keyword, int max_distance);
SearchResult* perform_search(const char** items, int items_count, const char* keyword, bool is_sorted, bool use_fuzzy, int max_distance);

#endif // SEARCH_H
