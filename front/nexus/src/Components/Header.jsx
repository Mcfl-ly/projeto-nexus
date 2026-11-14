import "../home_page/Home.css"
import claquete from "../assets/claquete-roxa.png";
import controle from "../assets/controle-azul.png";
import livro from "../assets/livro-vermelho.png";
import casinha from "../assets/casinha-verde.png";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import User from "../user_min_window/User.jsx"


export default function Header() {
    const [userName, setUserName] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        async function checkSession() {
            try {
                const response = await fetch("http://localhost:8000/users/me", {
                    credentials: "include",
                    signal: controller.signal,
                });

                if (!response.ok) {
                    throw new Error(`Erro ao buscar usuário: ${response.status}`);
                }

                const user = await response.json();
                setUserName(user.username);
            } catch (error) {
                if (error.name !== "AbortError") {
                    console.error(error);
                }
            }
        }

        checkSession();

        return () => controller.abort();
    }, []);


    return (
        <header className="site-header">
            <a className="logo" href="/" aria-label="Nexus — início">NEXUS</a>

            <nav aria-label="Navegação principal">
                <a className="home_button" href="/" aria-current="page">
                    <img src={casinha} alt="Home" alt="casa verde" width="20" height="20" />
                    Início</a>

                <Link className="movie_button" to="/filmes">
                    <img src={claquete} alt="Filmes" alt="claquete roxa" width="20" height="20" />
                    Filmes</Link>

                <a className="game_button" href="/jogos">
                    <img src={controle} alt="Jogos" alt="controle azul" width="20" height="20" />
                    Jogos</a>

                <a className="book_button" href="/livros">
                    <img src={livro} alt="Livros" alt="livro vermelho" width="20" height="20" />
                    Livros</a>
            </nav>

            {/*<form className="search" role="search" onSubmit={handleSearch} action="/busca">*/}
            {/*  <label className="sr-only" htmlFor="busca">Buscar no acervo</label>*/}
            {/*  <input*/}
            {/*      id="busca"*/}
            {/*      name="q"*/}
            {/*      type="search"*/}
            {/*      placeholder="Buscar em todo o acervo..."*/}
            {/*  />*/}
            {/*</form>*/}

            <div className="user-actions">

                {/*<button className="user_button" onClick={checkSession} type="button" aria-label="Abrir menu do perfil">*/}
                {/*    <img src={user_icon} alt="" width="36" height="36"/>*/}
                {/*</button>*/}
                <User usuario={userName} />
            </div>
        </header>
    )
}
