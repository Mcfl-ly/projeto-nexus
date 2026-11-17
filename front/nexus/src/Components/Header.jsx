import "../home_page/Home.css"
import claquete from "../assets/claquete-roxa.png";
import controle from "../assets/controle-azul.png";
import livro from "../assets/livro-vermelho.png";
import casinha from "../assets/casinha-verde.png";
import { Link, NavLink, useOutletContext } from "react-router-dom";
import User from "../user_min_window/User.jsx"


export default function Header({ username }) {
    const { user } = useOutletContext();
return (
        <header className="site-header">
            <Link className="logo" to="/" aria-label="Nexus — início">NEXUS</Link>

            <nav aria-label="Navegação principal">
                <NavLink className="home_button" to="/" end>
                    <img src={casinha} alt="casa verde" width="20" height="20" />
                    Início</NavLink>

                <Link className="movie_button" to="/filmes">
                    <img src={claquete} alt="claquete roxa" width="20" height="20" />
                    Filmes</Link>

                <NavLink className="game_button" to="/jogos">
                    <img src={controle} alt="controle azul" width="20" height="20" />
                    Jogos</NavLink>

                <NavLink className="book_button" to="/livros">
                    <img src={livro} alt="livro vermelho" width="20" height="20" />
                    Livros</NavLink>
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
                <User usuario={username ?? user?.username} />
            </div>
        </header>
    )
}
