"""学生信息管理系统 - 后端 API 服务"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection, init_db
from models import StudentCreate, StudentUpdate, StudentResponse

app = FastAPI(title="学生信息管理系统 API", version="1.0.0")

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ============================
# 健康检查
# ============================
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "学生信息管理系统"}


# ============================
# 查询学生列表 (支持搜索 + 分页)
# ============================
@app.get("/api/students")
def list_students(
    keyword: str = Query(default="", description="搜索关键词(姓名/专业/班级)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    with get_connection() as conn:
        cur = conn.cursor()
        if keyword:
            data_query = """SELECT id, name, gender, age, major, class_name, phone, email,
                       to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
                FROM students
                WHERE name LIKE %s OR major LIKE %s OR class_name LIKE %s
                ORDER BY id DESC LIMIT %s OFFSET %s"""
            count_query = "SELECT COUNT(*) FROM students WHERE name LIKE %s OR major LIKE %s OR class_name LIKE %s"
            params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            cur.execute(data_query, (*params, page_size, (page - 1) * page_size))
            rows = cur.fetchall()
            cur.execute(count_query, params)
            total = cur.fetchone()[0]
        else:
            cur.execute(
                """SELECT id, name, gender, age, major, class_name, phone, email,
                       to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
                FROM students ORDER BY id DESC LIMIT %s OFFSET %s""",
                (page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM students")
            total = cur.fetchone()[0]
        cur.close()

    students = []
    for row in rows:
        students.append({
            "id": row[0], "name": row[1], "gender": row[2],
            "age": row[3], "major": row[4], "class_name": row[5],
            "phone": row[6], "email": row[7], "created_at": row[8],
        })
    return {"total": total, "page": page, "page_size": page_size, "data": students}


# ============================
# 查询单个学生
# ============================
@app.get("/api/students/{student_id}")
def get_student(student_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, name, gender, age, major, class_name, phone, email,
                   to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
            FROM students WHERE id = %s""",
            (student_id,),
        )
        row = cur.fetchone()
        cur.close()
    if not row:
        raise HTTPException(status_code=404, detail="学生不存在")
    return {
        "id": row[0], "name": row[1], "gender": row[2],
        "age": row[3], "major": row[4], "class_name": row[5],
        "phone": row[6], "email": row[7], "created_at": row[8],
    }


# ============================
# 新增学生
# ============================
@app.post("/api/students", status_code=201)
def create_student(student: StudentCreate):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO students (name, gender, age, major, class_name, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (student.name, student.gender, student.age, student.major,
             student.class_name, student.phone, student.email),
        )
        new_id = cur.fetchone()[0]
        cur.close()
    return {"message": "学生添加成功", "id": new_id}


# ============================
# 更新学生
# ============================
@app.put("/api/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="学生不存在")

        updates = student.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="没有需要更新的字段")

        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [student_id]
        cur.execute(f"UPDATE students SET {set_clause} WHERE id = %s", values)
        cur.close()
    return {"message": "学生信息更新成功"}


# ============================
# 删除学生
# ============================
@app.delete("/api/students/{student_id}")
def delete_student(student_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE id = %s", (student_id,))
        if not cur.fetchone():
            cur.close()
            raise HTTPException(status_code=404, detail="学生不存在")
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        cur.close()
    return {"message": "学生删除成功"}
