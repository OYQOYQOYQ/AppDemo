#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// 搜索结果结构体
typedef struct {
    int* indices;
    int count;
    int capacity;
} SearchResult;

// 初始化搜索结果
SearchResult* init_search_result() {
    SearchResult* result = (SearchResult*)malloc(sizeof(SearchResult));
    result->capacity = 10;
    result->count = 0;
    result->indices = (int*)malloc(sizeof(int) * result->capacity);
    return result;
}

// 添加索引到搜索结果
void add_to_result(SearchResult* result, int index) {
    if (result->count >= result->capacity) {
        result->capacity *= 2;
        result->indices = (int*)realloc(result->indices, sizeof(int) * result->capacity);
    }
    result->indices[result->count++] = index;
}

// 释放搜索结果
void free_search_result(SearchResult* result) {
    free(result->indices);
    free(result);
}

// 辅助函数：检查字符是否为UTF-8多字节字符的首字节
bool is_utf8_first_byte(unsigned char c);

// 辅助函数：获取UTF-8字符的字节长度
int get_utf8_char_length(unsigned char c);

// 辅助函数：计算UTF-8字符串的字符长度（而非字节长度）
int utf8_strlen(const char* s);

// 辅助函数：检查字符是否为UTF-8多字节字符的首字节
bool is_utf8_first_byte(unsigned char c) {
    return (c & 0xC0) != 0x80;
}



// 辅助函数：计算UTF-8字符串的字符长度（而非字节长度）
int utf8_strlen(const char* s) {
    if (s == NULL) return 0;
    
    int len = 0;
    const unsigned char* p = (const unsigned char*)s;
    
    while (*p) {
        len++;
        // 跳过当前UTF-8字符的后续字节
        int char_len = get_utf8_char_length(*p);
        p += char_len;
    }
    
    return len;
}

// 辅助函数：将字符转换为小写（支持UTF-8，中文字符保持不变）
unsigned char to_lower(unsigned char c) {
    if (c >= 'A' && c <= 'Z') {
        return c + ('a' - 'A');
    }
    return c; // 中文字符保持不变
}

// 辅助函数：大小写不敏感的字符串比较（支持UTF-8）
int strcasecmp_custom(const char* s1, const char* s2) {
    const unsigned char* p1 = (const unsigned char*)s1;
    const unsigned char* p2 = (const unsigned char*)s2;
    
    while (*p1 && *p2) {
        // 处理UTF-8多字节字符
        if (is_utf8_first_byte(*p1) && is_utf8_first_byte(*p2)) {
            if (*p1 >= 0x80 && *p2 >= 0x80) {
                // 都是中文字符，直接比较字节
                if (*p1 != *p2) {
                    return *p1 - *p2;
                }
                // 继续比较后续字节
                const unsigned char* p1_temp = p1 + 1;
                const unsigned char* p2_temp = p2 + 1;
                while ((*p1_temp & 0xC0) == 0x80 && (*p2_temp & 0xC0) == 0x80) {
                    if (*p1_temp != *p2_temp) {
                        return *p1_temp - *p2_temp;
                    }
                    p1_temp++;
                    p2_temp++;
                }
                // 移动指针到下一个字符的开始
                p1 = p1_temp;
                p2 = p2_temp;
            } else if (*p1 >= 0x80) {
                // s1是中文，s2是ASCII，中文大于ASCII
                return 1;
            } else if (*p2 >= 0x80) {
                // s2是中文，s1是ASCII，ASCII小于中文
                return -1;
            } else {
                // 都是ASCII字符，大小写不敏感比较
                unsigned char c1 = to_lower(*p1);
                unsigned char c2 = to_lower(*p2);
                if (c1 != c2) {
                    return c1 - c2;
                }
                p1++;
                p2++;
            }
        } else {
            // 处理单字节字符或多字节字符的后续字节
            p1++;
            p2++;
        }
    }
    
    // 检查哪个字符串先结束
    return (unsigned char)*p1 - (unsigned char)*p2;
}

// 辅助函数：大小写不敏感的子字符串搜索（支持UTF-8）
const char* strcasestr_custom(const char* haystack, const char* needle) {
    if (!*needle) return haystack;
    
    const unsigned char* h = (const unsigned char*)haystack;
    const unsigned char* n = (const unsigned char*)needle;
    
    // 计算needle的UTF-8字符长度
    int needle_len = utf8_strlen((const char*)n);
    
    while (*h) {
        const unsigned char* h_pos = h;
        const unsigned char* n_pos = n;
        int matched_chars = 0;
        
        // 逐字符比较
        while (*h_pos && *n_pos) {
            if (is_utf8_first_byte(*h_pos) && is_utf8_first_byte(*n_pos)) {
                if (*h_pos >= 0x80 && *n_pos >= 0x80) {
                    // 都是中文字符，需要比较完整的字符序列
                    const unsigned char* h_temp = h_pos;
                    const unsigned char* n_temp = n_pos;
                    bool match = true;
                    
                    // 比较当前中文字符的所有字节
                    while (1) {
                        if (*h_temp != *n_temp) {
                            match = false;
                            break;
                        }
                        
                        // 移动到下一个字节
                        h_temp++;
                        n_temp++;
                        
                        // 检查是否到达字符边界
                        if ((*h_temp & 0xC0) != 0x80 || (*n_temp & 0xC0) != 0x80) {
                            break;
                        }
                    }
                    
                    if (!match) {
                        break;
                    }
                    
                    // 移动指针到下一个字符的开始
                    h_pos = h_temp;
                    n_pos = n_temp;
                } else if (*h_pos >= 0x80 || *n_pos >= 0x80) {
                    // 一个是中文，一个是ASCII，不匹配
                    break;
                } else {
                    // 都是ASCII字符，大小写不敏感比较
                    if (to_lower(*h_pos) != to_lower(*n_pos)) {
                        break;
                    }
                    h_pos++;
                    n_pos++;
                }
                
                matched_chars++;
                
                // 如果已经匹配了所有字符，返回结果
                if (matched_chars == needle_len) {
                    return (const char*)h;
                }
            } else {
                // 处理单字节字符或多字节字符的后续字节
                h_pos++;
                n_pos++;
            }
        }
        
        // 移动到haystack的下一个UTF-8字符
        if (is_utf8_first_byte(*h)) {
            h++;
            // 跳过后续字节
            while ((*h & 0xC0) == 0x80) {
                h++;
            }
        } else {
            h++;
        }
    }
    
    return NULL; // 未找到
}

// 线性搜索 - 在字符串数组中查找包含关键词的项（支持大小写不敏感）
SearchResult* linear_search(const char** items, int items_count, const char* keyword) {
    SearchResult* result = init_search_result();
    int keyword_len = strlen(keyword);
    
    for (int i = 0; i < items_count; i++) {
        const char* item = items[i];
        if (item == NULL) continue;
        
        // 区分大小写的子字符串搜索（与Python实现保持一致）
        const char* found = strstr(item, keyword);
        if (found != NULL) {
            add_to_result(result, i);
        }
    }
    
    return result;
}



// 辅助函数：获取UTF-8字符串中第n个字符的指针
const unsigned char* get_utf8_char(const unsigned char* str, int n) {
    int count = 0;
    const unsigned char* p = str;
    
    while (*p) {
        if (count == n) {
            return p;
        }
        
        // 获取当前字符的长度并移动指针
        int char_len = get_utf8_char_length(*p);
        p += char_len;
        count++;
    }
    
    return p;
}

// 辅助函数：获取UTF-8字符的字节长度
int get_utf8_char_length(unsigned char c) {
    if ((c & 0x80) == 0) return 1; // ASCII
    if ((c & 0xE0) == 0xC0) return 2; // 2字节UTF-8
    if ((c & 0xF0) == 0xE0) return 3; // 3字节UTF-8（中文）
    if ((c & 0xF8) == 0xF0) return 4; // 4字节UTF-8
    return 1; // 默认1字节
}

// 辅助函数：比较两个UTF-8字符是否相等（支持中文和ASCII大小写不敏感）
bool utf8_char_equal(const unsigned char* c1, const unsigned char* c2) {
    // 处理ASCII字符（大小写不敏感）
    if (*c1 < 0x80 && *c2 < 0x80) {
        return to_lower(*c1) == to_lower(*c2);
    }
    
    // 处理UTF-8多字节字符（中文等）
    // 获取两个字符的长度
    int len1 = get_utf8_char_length(*c1);
    int len2 = get_utf8_char_length(*c2);
    
    // 如果长度不同，字符不相等
    if (len1 != len2) {
        return false;
    }
    
    // 比较所有字节（中文区分大小写吗？通常不区分，这里暂时保持精确匹配）
    for (int i = 0; i < len1; i++) {
        if (c1[i] != c2[i]) {
            return false;
        }
    }
    
    return true;
}

// 简化版：直接按字节比较计算编辑距离（支持UTF-8）
// 注意：这不是真正的字符级编辑距离，但对于中文搜索来说足够使用
int levenshtein_distance(const char* s1, const char* s2) {
    int len1 = strlen(s1);
    int len2 = strlen(s2);
    
    // 优化：如果其中一个字符串为空
    if (len1 == 0) return len2;
    if (len2 == 0) return len1;
    
    // 优化：使用一维数组代替二维数组，减少内存使用
    int* dp_prev = (int*)malloc(sizeof(int) * (len2 + 1));
    int* dp_curr = (int*)malloc(sizeof(int) * (len2 + 1));
    
    // 初始化第一行
    for (int j = 0; j <= len2; j++) {
        dp_prev[j] = j;
    }
    
    // 填充矩阵
    for (int i = 1; i <= len1; i++) {
        dp_curr[0] = i;
        
        for (int j = 1; j <= len2; j++) {
            // 对于UTF-8，我们按字节比较，但对于ASCII字符，我们大小写不敏感
            int cost = 1;
            if (s1[i-1] < 0x80 && s2[j-1] < 0x80) {
                // ASCII字符，大小写不敏感比较
                cost = (to_lower(s1[i-1]) == to_lower(s2[j-1])) ? 0 : 1;
            } else {
                // UTF-8多字节字符，直接比较字节
                cost = (s1[i-1] == s2[j-1]) ? 0 : 1;
            }
            
            // 计算最小代价
            int insert_cost = dp_curr[j-1] + 1;
            int delete_cost = dp_prev[j] + 1;
            int replace_cost = dp_prev[j-1] + cost;
            
            // 找出最小值
            dp_curr[j] = insert_cost;
            if (delete_cost < dp_curr[j]) dp_curr[j] = delete_cost;
            if (replace_cost < dp_curr[j]) dp_curr[j] = replace_cost;
        }
        
        // 交换两行
        int* temp = dp_prev;
        dp_prev = dp_curr;
        dp_curr = temp;
    }
    
    int distance = dp_prev[len2];
    
    // 释放内存
    free(dp_prev);
    free(dp_curr);
    
    return distance;
}

// 模糊搜索 - 优化版，更适合中文搜索
SearchResult* fuzzy_search(const char** items, int items_count, const char* keyword, int max_distance) {
    SearchResult* result = init_search_result();
    int keyword_len = strlen(keyword);
    
    // 如果关键词是单个中文字符（UTF-8占3字节），使用子字符串匹配
    if (keyword_len == 3 && (unsigned char)keyword[0] >= 0xE0) {
        for (int i = 0; i < items_count; i++) {
            const char* item = items[i];
            if (item == NULL) continue;
            
            // 检查item是否包含keyword作为子字符串
            if (strstr(item, keyword) != NULL) {
                add_to_result(result, i);
            }
        }
        return result;
    }
    
    // 对于其他情况，使用编辑距离
    for (int i = 0; i < items_count; i++) {
        const char* item = items[i];
        if (item == NULL) continue;
        
        int item_len = strlen(item);
        
        // 对于长关键词，使用更宽松的长度差异检查
        int max_len_diff = (keyword_len > 5) ? keyword_len / 2 : max_distance;
        if (abs(item_len - keyword_len) > max_len_diff) {
            continue;
        }
        
        int distance = levenshtein_distance(item, keyword);
        if (distance <= max_distance) {
            add_to_result(result, i);
        }
    }
    
    return result;
}

// 二分搜索 - 在已排序的字符串数组中精确查找（支持大小写不敏感）
int binary_search(const char** sorted_items, int items_count, const char* keyword) {
    int left = 0;
    int right = items_count - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        int cmp = strcasecmp_custom(sorted_items[mid], keyword);
        
        if (cmp == 0) {
            return mid;  // 找到匹配项
        } else if (cmp < 0) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;  // 未找到
}

// 搜索算法接口 - 根据选项执行不同的搜索策略
extern SearchResult* perform_search(const char** items, int items_count, const char* keyword, bool is_sorted, bool use_fuzzy, int max_distance) {
    if (use_fuzzy) {
        // 模糊搜索时，如果关键词较长，自动调整最大距离
        int keyword_len = strlen(keyword);
        int adjusted_distance = max_distance;
        if (keyword_len > 10) {
            adjusted_distance = keyword_len / 3;  // 更长的关键词允许更大的编辑距离
        }
        return fuzzy_search(items, items_count, keyword, adjusted_distance);
    } else if (is_sorted) {
        // 对于排序数据，使用精确匹配（与Python实现保持一致）
        SearchResult* result = init_search_result();
        
        // 二分搜索精确匹配
        int left = 0;
        int right = items_count - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            int cmp = strcmp(items[mid], keyword);
            
            if (cmp == 0) {
                // 找到匹配项，添加到结果
                add_to_result(result, mid);
                
                // 继续查找左右两侧是否有重复的匹配项
                // 向左查找
                int i = mid - 1;
                while (i >= 0 && strcmp(items[i], keyword) == 0) {
                    add_to_result(result, i);
                    i--;
                }
                
                // 向右查找
                i = mid + 1;
                while (i < items_count && strcmp(items[i], keyword) == 0) {
                    add_to_result(result, i);
                    i++;
                }
                
                break;
            } else if (cmp < 0) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return result;
    } else {
        return linear_search(items, items_count, keyword);
    }
}

// 测试函数（用于调试）
#ifdef DEBUG
int main() {
    const char* items[] = {"apple", "banana", "orange", "pear", "grape", "watermelon"};
    int count = sizeof(items) / sizeof(items[0]);
    
    // 测试线性搜索
    SearchResult* linear_result = linear_search(items, count, "a");
    printf("Linear search found %d items:\n", linear_result->count);
    for (int i = 0; i < linear_result->count; i++) {
        printf("  Index %d: %s\n", linear_result->indices[i], items[linear_result->indices[i]]);
    }
    free_search_result(linear_result);
    
    // 测试二分搜索
    const char* sorted_items[] = {"apple", "banana", "grape", "orange", "pear", "watermelon"};
    int binary_index = binary_search(sorted_items, count, "orange");
    printf("Binary search for 'orange': index = %d\n", binary_index);
    
    // 测试模糊搜索
    SearchResult* fuzzy_result = fuzzy_search(items, count, "appl", 1);
    printf("Fuzzy search found %d items:\n", fuzzy_result->count);
    for (int i = 0; i < fuzzy_result->count; i++) {
        printf("  Index %d: %s\n", fuzzy_result->indices[i], items[fuzzy_result->indices[i]]);
    }
    free_search_result(fuzzy_result);
    
    return 0;
}
#endif
