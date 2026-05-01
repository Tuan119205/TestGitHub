import flask
import pyodbc

app = flask.Flask(__name__)

cn_str = (
    "Driver={SQL Server};"
    "Server=DESKTOP-8FG65QA\\SQLEXPRESS;"
    "Database=DuLieu1;"
    "Trusted_Connection=yes;"
)

def get_conn():
    return pyodbc.connect(cn_str)
@app.route('/')
def home():
    return "API đang chạy OK"
# =========================
# GET ALL (chỉ lấy chưa xóa)
# =========================
@app.route('/kh', methods=['GET'])
def get_all():
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblKhach WHERE isDeleted = 0")

        keys = [i[0] for i in cursor.description]
        data = [dict(zip(keys, row)) for row in cursor.fetchall()]

        return flask.jsonify(data), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================
# GET BY ID
# =========================
@app.route('/kh/<int:id>', methods=['GET'])
def get_by_id(id):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tblKhach WHERE MaKhach = ? AND isDeleted = 0",
            (id,)
        )

        row = cursor.fetchone()
        if not row:
            return flask.jsonify({"mess": "không tìm thấy"}), 404

        keys = [i[0] for i in cursor.description]
        result = dict(zip(keys, row))

        return flask.jsonify(result), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================
# ADD (không cần MaKhach)
# =========================
@app.route('/kh', methods=['POST'])
def add_kh():
    conn = get_conn()
    try:
        data = flask.request.json

        tk = data.get("TenKhach")
        gt = data.get("GioiTinh")
        ns = data.get("NgaySinh")   # format: YYYY-MM-DD
        dc = data.get("DiaChi")
        dt = data.get("DienThoai")
        email = data.get("Email")

        cursor = conn.cursor()
        sql = """
        INSERT INTO tblKhach
        (TenKhach, GioiTinh, NgaySinh, DiaChi, DienThoai, Email)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (tk, gt, ns, dc, dt, email))
        conn.commit()

        return flask.jsonify({"mess": "thêm thành công"}), 201
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================
# UPDATE
# =========================
@app.route('/kh/<int:id>', methods=['PUT'])
def update_kh(id):
    conn = get_conn()
    try:
        data = flask.request.json

        tk = data.get("TenKhach")
        gt = data.get("GioiTinh")
        ns = data.get("NgaySinh")
        dc = data.get("DiaChi")
        dt = data.get("DienThoai")
        email = data.get("Email")

        cursor = conn.cursor()
        sql = """
        UPDATE tblKhach
        SET TenKhach=?, GioiTinh=?, NgaySinh=?, DiaChi=?, DienThoai=?, Email=?
        WHERE MaKhach=? AND isDeleted = 0
        """
        cursor.execute(sql, (tk, gt, ns, dc, dt, email, id))
        conn.commit()

        return flask.jsonify({"mess": "cập nhật thành công"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================
# DELETE (soft delete)
# =========================
@app.route('/kh/<int:id>', methods=['DELETE'])
def delete_kh(id):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        sql = "UPDATE tblKhach SET isDeleted = 1 WHERE MaKhach = ?"
        cursor.execute(sql, (id,))
        conn.commit()

        return flask.jsonify({"mess": "xóa thành công"}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================
# SEARCH (bonus)
# =========================
@app.route('/kh/search', methods=['GET'])
def search_kh():
    conn = get_conn()
    try:
        ten = flask.request.args.get("ten", "")
        gt = flask.request.args.get("gioitinh", "")

        cursor = conn.cursor()
        sql = """
        SELECT * FROM tblKhach
        WHERE isDeleted = 0
        AND TenKhach LIKE ?
        AND GioiTinh LIKE ?
        """
        cursor.execute(sql, (f"%{ten}%", f"%{gt}%"))

        keys = [i[0] for i in cursor.description]
        data = [dict(zip(keys, row)) for row in cursor.fetchall()]

        return flask.jsonify(data), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)