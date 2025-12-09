#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// 平台特定的头文件
#ifdef _WIN32
#include <windows.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#define MAX_PATH 1024
#endif

// 平台特定的函数导出
#ifdef _WIN32
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

// 跨平台的不区分大小写字符串比较
#ifdef _WIN32
#define strcasecmp strcmpi
#else
#include <strings.h>
#endif

// 用于存储扫描结果的结构体
struct ScanResult {
    char** files;
    int count;
    int capacity;
};

// 初始化扫描结果
void init_scan_result(struct ScanResult* result) {
    result->count = 0;
    result->capacity = 1000;
    result->files = (char**)malloc(result->capacity * sizeof(char*));
}

// 添加文件到扫描结果
void add_file(struct ScanResult* result, const char* filepath) {
    if (result->count >= result->capacity) {
        // 扩容
        result->capacity *= 2;
        result->files = (char**)realloc(result->files, result->capacity * sizeof(char*));
    }
    result->files[result->count] = (char*)malloc((strlen(filepath) + 1) * sizeof(char));
    strcpy(result->files[result->count], filepath);
    result->count++;
}

// 检查文件扩展名是否在允许列表中
int is_extension_allowed(const char* filename, const char** allowed_extensions, int extension_count) {
    if (allowed_extensions == NULL || extension_count == 0) {
        return 1;  // 允许所有文件
    }
    
    const char* dot = strrchr(filename, '.');
    if (dot == NULL) {
        return 0;  // 没有扩展名，不允许
    }
    
    const char* extension = dot + 1;
    for (int i = 0; i < extension_count; i++) {
        if (strcasecmp(extension, allowed_extensions[i]) == 0) {
            return 1;
        }
    }
    
    return 0;
}

// 递归扫描目录的Windows实现
#ifdef _WIN32
void scan_directory(const char* directory, int current_depth, int max_depth, 
                    const char** allowed_extensions, int extension_count, 
                    struct ScanResult* result) {
    if (current_depth > max_depth) {
        return;
    }
    
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = INVALID_HANDLE_VALUE;
    char searchPath[MAX_PATH];
    
    // 构造搜索路径
    snprintf(searchPath, MAX_PATH, "%s\\*", directory);
    
    hFind = FindFirstFile(searchPath, &findFileData);
    
    if (hFind == INVALID_HANDLE_VALUE) {
        return;
    }
    
    do {
        // 跳过 . 和 ..
        if (strcmp(findFileData.cFileName, ".") == 0 || strcmp(findFileData.cFileName, "..") == 0) {
            continue;
        }
        
        // 构造完整路径
        char fullPath[MAX_PATH];
        snprintf(fullPath, MAX_PATH, "%s\\%s", directory, findFileData.cFileName);
        
        if (findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            // 递归扫描子目录
            scan_directory(fullPath, current_depth + 1, max_depth, 
                          allowed_extensions, extension_count, result);
        } else {
            // 检查文件扩展名
            if (is_extension_allowed(findFileData.cFileName, allowed_extensions, extension_count)) {
                add_file(result, fullPath);
            }
        }
    } while (FindNextFile(hFind, &findFileData) != 0);
    
    FindClose(hFind);
}
#else
// 递归扫描目录的POSIX实现
void scan_directory(const char* directory, int current_depth, int max_depth, 
                    const char** allowed_extensions, int extension_count, 
                    struct ScanResult* result) {
    if (current_depth > max_depth) {
        return;
    }
    
    DIR* dir = opendir(directory);
    if (dir == NULL) {
        return;
    }
    
    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        // 跳过 . 和 ..
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        
        // 构造完整路径
        char fullPath[MAX_PATH];
        snprintf(fullPath, MAX_PATH, "%s/%s", directory, entry->d_name);
        
        // 检查是否为目录
        struct stat fileStat;
        if (stat(fullPath, &fileStat) == 0) {
            if (S_ISDIR(fileStat.st_mode)) {
                // 递归扫描子目录
                scan_directory(fullPath, current_depth + 1, max_depth, 
                              allowed_extensions, extension_count, result);
            } else {
                // 检查文件扩展名
                if (is_extension_allowed(entry->d_name, allowed_extensions, extension_count)) {
                    add_file(result, fullPath);
                }
            }
        }
    }
    
    closedir(dir);
}
#endif

// 导出函数：扫描目录
DLL_EXPORT char** scan_directory_c(const char* directory, int depth, 
                                  const char** allowed_extensions, int extension_count, 
                                  int* file_count) {
    struct ScanResult result;
    init_scan_result(&result);
    
    scan_directory(directory, 0, depth, allowed_extensions, extension_count, &result);
    
    *file_count = result.count;
    return result.files;
}

// 导出函数：释放扫描结果
DLL_EXPORT void free_scan_result(char** files, int file_count) {
    if (files == NULL) {
        return;
    }
    
    for (int i = 0; i < file_count; i++) {
        free(files[i]);
    }
    free(files);
}
