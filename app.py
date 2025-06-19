from flask import Flask, render_template, request, jsonify, redirect, url_for
import psycopg2
from datetime import datetime, date
import os

app = Flask(_name_)

# Configuracao do banco de dados
DATABASE_CONFIG = {
    'user': 'postgres',
    'host': 'localhost',
    'password': '123456',
    'port': '5432',
    'database': 'manutencao_db',
}

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

@app.route('/')
def dashboard():
    """Pagina principal - Dashboard"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        
        # Estatisticas para o dashboard
        cur.execute("SELECT COUNT(*) FROM maquina")
        total_maquinas = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM tecnico")
        total_tecnicos = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM agendamento WHERE cod_status = 1")
        agendamentos_pendentes = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM execucao WHERE cod_status = 3")
        execucoes_concluidas = cur.fetchone()[0]
        
        # ultimas execucoes
        cur.execute("""
            SELECT e.id_execucao, e.data_realizada, m.nome_maquina, t.nome_tecnico, s.desc_status
            FROM execucao e
            JOIN agendamento a ON e.cod_agendamento = a.id_agendamento
            JOIN maquina m ON a.cod_maquina = m.id_maquina
            JOIN tecnico t ON a.cod_tecnico = t.id_tecnico
            JOIN status s ON e.cod_status = s.id_status
            ORDER BY e.data_realizada DESC
            LIMIT 5
        """)
        ultimas_execucoes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('dashboard.html', 
                             total_maquinas=total_maquinas,
                             total_tecnicos=total_tecnicos,
                             agendamentos_pendentes=agendamentos_pendentes,
                             execucoes_concluidas=execucoes_concluidas,
                             ultimas_execucoes=ultimas_execucoes)
    
    return render_template('dashboard.html')

@app.route('/maquinas')
def maquinas():
    """Pagina de gestao de maquinas"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_maquina, m.nome_maquina, s.nome_setor
            FROM maquina m
            JOIN setor s ON m.cod_setor = s.id_setor
            ORDER BY m.nome_maquina
        """)
        maquinas_list = cur.fetchall()
        
        cur.execute("SELECT id_setor, nome_setor FROM setor ORDER BY nome_setor")
        setores = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('maquinas.html', maquinas=maquinas_list, setores=setores)
    
    return render_template('maquinas.html')

@app.route('/tecnicos')
def tecnicos():
    """Pagina de gestao de tecnicos"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id_tecnico, t.nome_tecnico, s.nome_setor, t.valorhora, t.cpf, t.telefone
            FROM tecnico t
            JOIN setor s ON t.cod_setor = s.id_setor
            ORDER BY t.nome_tecnico
        """)
        tecnicos_list = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('tecnicos.html', tecnicos=tecnicos_list)
    
    return render_template('tecnicos.html')

@app.route('/materiais')
def materiais():
    """Pagina de gestao de materiais"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_material, m.nome_material, m.descricao_material, m.valor_material,
                   COALESCE(e.qntd_estoque, 0) as estoque
            FROM material m
            LEFT JOIN estoque e ON m.id_material = e.cod_material
            ORDER BY m.nome_material
        """)
        materiais_list = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('materiais.html', materiais=materiais_list)
    
    return render_template('materiais.html')

@app.route('/agendamentos')
def agendamentos():
    """Pagina de gestao de agendamentos"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id_agendamento, a.data_prevista, a.hora_prevista,
                   m.nome_maquina, t.nome_tecnico, tm.descricao, s.desc_status
            FROM agendamento a
            JOIN maquina m ON a.cod_maquina = m.id_maquina
            JOIN tecnico t ON a.cod_tecnico = t.id_tecnico
            JOIN tipo_manutencao tm ON a.cod_tipo_manut = tm.id_tipo_manut
            JOIN status s ON a.cod_status = s.id_status
            ORDER BY a.data_prevista DESC
        """)
        agendamentos_list = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('agendamentos.html', agendamentos=agendamentos_list)
    
    return render_template('agendamentos.html')

@app.route('/execucoes')
def execucoes():
    """Pagina de gestao de execucoes"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id_execucao, e.data_realizada, e.hora_inicio, e.hora_fim,
                   e.valor_exec, m.nome_maquina, t.nome_tecnico, s.desc_status
            FROM execucao e
            JOIN agendamento a ON e.cod_agendamento = a.id_agendamento
            JOIN maquina m ON a.cod_maquina = m.id_maquina
            JOIN tecnico t ON a.cod_tecnico = t.id_tecnico
            JOIN status s ON e.cod_status = s.id_status
            ORDER BY e.data_realizada DESC
        """)
        execucoes_list = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('execucoes.html', execucoes=execucoes_list)
    
    return render_template('execucoes.html')

if _name_ == '_main_':
    app.run(debug=True)
