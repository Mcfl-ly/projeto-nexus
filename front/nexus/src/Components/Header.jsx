import "../home_page/Home.css"
import user_icon from "../assets/user_icon.png";
import claquete from "../assets/claquete-roxa.png";
import controle from "../assets/controle-azul.png";
import livro from "../assets/livro-vermelho.png";
import casinha from "../assets/casinha-verde.png";
import { Link } from "react-router-dom";
import {useState} from "react";

function Header() {
    const controller = new AbortController();
    async function checkSession() {
        try {
            const response = await fetch("http://localhost:8000/users/me", {

                credentials: "include",
                signal: controller.signal,
            });

            if (response.ok) {
                const user = await response.json();
                console.log(user);
            }
        } catch (error) {
            console.log(error);
        }

    }


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

                <button className="user_button" onClick={checkSession} type="button" aria-label="Abrir menu do perfil">
                    <img src={user_icon} alt="" width="36" height="36"/>
                </button>
            </div>
        </header>
    )
}

export default Header;