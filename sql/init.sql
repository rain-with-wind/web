-- 学生信息管理系统 - 数据库初始化脚本
-- 适用于 openGauss/GaussDB (兼容 PostgreSQL)

CREATE TABLE IF NOT EXISTS students (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    gender      VARCHAR(10)  DEFAULT '男',
    age         INTEGER      DEFAULT 20,
    major       VARCHAR(100) DEFAULT '计算机科学与技术',
    class_name  VARCHAR(100) DEFAULT '',
    phone       VARCHAR(20)  DEFAULT '',
    email       VARCHAR(100) DEFAULT '',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 插入一些示例数据
INSERT INTO students (name, gender, age, major, class_name, phone, email) VALUES
('张三', '男', 21, '计算机科学与技术', '计科2101', '13800138001', 'zhangsan@whu.edu.cn'),
('李四', '女', 20, '软件工程', '软工2102', '13800138002', 'lisi@whu.edu.cn'),
('王五', '男', 22, '数据科学与大数据技术', '大数据2101', '13800138003', 'wangwu@whu.edu.cn');
