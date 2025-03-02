package com.example.sorting;

// 文件编码：UTF-8
public class SortingAlgorithms {
    
    /**
     * 冒泡排序
     * 时间复杂度：O(n²)
     * 空间复杂度：O(1)
     * 算法思想：通过相邻元素的比较和交换，将最大的元素逐步冒泡到数组末尾
     */
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                // 如果前面的元素大于后面的元素，则交换它们的位置
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    /**
     * 选择排序
     * 时间复杂度：O(n²)
     * 空间复杂度：O(1)
     * 算法思想：每次从未排序区间选择最小的元素，放到已排序区间的末尾
     */
    public static void selectionSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            // 找到未排序区间中最小元素的下标
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }
            // 将找到的最小元素与未排序区间的第一个元素交换
            int temp = arr[minIdx];
            arr[minIdx] = arr[i];
            arr[i] = temp;
        }
    }

    /**
     * 插入排序
     * 时间复杂度：O(n²)
     * 空间复杂度：O(1)
     * 算法思想：将一个元素插入到已经排好序的数组中的适当位置
     */
    public static void insertionSort(int[] arr) {
        int n = arr.length;
        for (int i = 1; i < n; i++) {
            // 保存当前要插入的元素
            int key = arr[i];
            int j = i - 1;
            // 寻找插入位置并移动元素
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j = j - 1;
            }
            // 插入元素
            arr[j + 1] = key;
        }
    }

    /**
     * 快速排序
     * 时间复杂度：平均O(nlogn)，最坏O(n²)
     * 空间复杂度：O(logn)
     * 算法思想：选择一个基准元素，将数组分为两部分，一部分比基准小，另一部分比基准大
     */
    public static void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            // 获取分区点
            int pi = partition(arr, low, high);
            // 递归排序左右两部分
            quickSort(arr, low, pi - 1);
            quickSort(arr, pi + 1, high);
        }
    }

    /**
     * 快速排序的分区函数
     * 返回分区点的位置
     */
    private static int partition(int[] arr, int low, int high) {
        // 选择最后一个元素作为基准
        int pivot = arr[high];
        int i = (low - 1); // 小于基准的区域边界
        
        // 遍历数组，将小于基准的元素放到左边
        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        // 将基准元素放到正确的位置
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        return i + 1;
    }

    /**
     * 归并排序
     * 时间复杂度：O(nlogn)
     * 空间复杂度：O(n)
     * 算法思想：将数组分成两半，分别排序，然后合并两个有序数组
     */
    public static void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            // 计算中间点
            int middle = (left + right) / 2;
            // 递归排序左右两半
            mergeSort(arr, left, middle);
            mergeSort(arr, middle + 1, right);
            // 合并两个有序数组
            merge(arr, left, middle, right);
        }
    }

    /**
     * 归并排序的合并函数
     * 合并两个有序数组
     */
    private static void merge(int[] arr, int left, int middle, int right) {
        // 计算两个子数组的大小
        int n1 = middle - left + 1;
        int n2 = right - middle;

        // 创建临时数组
        int[] L = new int[n1];
        int[] R = new int[n2];

        // 将数据复制到临时数组
        for (int i = 0; i < n1; i++)
            L[i] = arr[left + i];
        for (int j = 0; j < n2; j++)
            R[j] = arr[middle + 1 + j];

        // 合并临时数组
        int i = 0, j = 0; // 初始化两个数组的索引
        int k = left; // 初始化合并数组的索引

        // 比较两个数组的元素并合并
        while (i < n1 && j < n2) {
            if (L[i] <= R[j]) {
                arr[k] = L[i];
                i++;
            } else {
                arr[k] = R[j];
                j++;
            }
            k++;
        }

        // 复制剩余的元素
        while (i < n1) {
            arr[k] = L[i];
            i++;
            k++;
        }
        while (j < n2) {
            arr[k] = R[j];
            j++;
            k++;
        }
    }

    /**
     * 打印数组的工具方法
     */
    public static void printArray(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i] + " ");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        // 测试数据
        int[] arr1 = {64, 34, 25, 12, 22, 11, 90};
        int[] arr2 = arr1.clone();
        int[] arr3 = arr1.clone();
        int[] arr4 = arr1.clone();
        int[] arr5 = arr1.clone();

        System.out.println("原始数组：");
        printArray(arr1);

        System.out.println("\n冒泡排序后：");
        bubbleSort(arr1);
        printArray(arr1);

        System.out.println("\n选择排序后：");
        selectionSort(arr2);
        printArray(arr2);

        System.out.println("\n插入排序后：");
        insertionSort(arr3);
        printArray(arr3);

        System.out.println("\n快速排序后：");
        quickSort(arr4, 0, arr4.length - 1);
        printArray(arr4);

        System.out.println("\n归并排序后：");
        mergeSort(arr5, 0, arr5.length - 1);
        printArray(arr5);
    }
} 