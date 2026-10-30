import { Link } from "react-router-dom";
import bttf from "../assets/bttf.jpg";
import "./Movies.css";
import Header from '../components/Header.jsx'
export default function Movies() {
    return (

        <>
        <Header />
        <div className="movies-page">
            {/* Cabeçalho */}


            <main className="movies-content">
                {/* Título da página */}
                <section className="movies-heading" aria-labelledby="movies-title">
                    <div>
                        <h1 id="movies-title">🎬 Meus filmes</h1>
                        <p>Organize o que quer assistir e acompanhe o que já viu.</p>
                    </div>

                    <button className="add-movie-button" type="button">
                        + Adicionar filme
                    </button>
                </section>

                <div className="movies-columns">
                    {/* Filmes que deseja assistir */}
                    <section className="movie-column" aria-labelledby="watchlist-title">
                        <header className="column-header">
                            <h2 id="watchlist-title">
                                <span className="status-dot status-pending" />
                                Quero assistir
                            </h2>

                            <span className="movie-count">filmes nessa classe (INT)</span>
                        </header>

                        <ul className="movie-list">
                            <li>
                                <article className="movie-card">
                                    <div className="movie-poster">
                                        <img src={bttf} alt="poster" />
                                        Capa</div>

                                    <div className="movie-info">
                                        <h3>Titulo do filme</h3>
                                        <p className="movie-year">ano do filme</p>

                                        <ul className="movie-genres" aria-label="Gêneros">
                                            <li>genero1</li>
                                            <li>genero2</li>
                                        </ul>
                                    </div>

                                    <div className="movie-actions">
                                        <button
                                            type="button"
                                            aria-label="Favoritar"
                                            aria-pressed={false}
                                        >
                                            ♡
                                        </button>

                                        <button
                                            type="button"
                                            aria-label="Mais opções"
                                        >
                                            ⋮
                                        </button>
                                    </div>
                                </article>
                            </li>

                        </ul>
                    </section>

                    {/* Filmes já assistidos */}
                    <section className="movie-column" aria-labelledby="watched-title">
                        <header className="column-header">
                            <h2 id="watched-title">
                                <span className="status-dot status-watched" />
                                Assistidos
                            </h2>

                            <span className="movie-count">filmes nessa classe (INT)</span>
                        </header>

                        <ul className="movie-list">
                            <li>
                                <article className="movie-card">
                                    <div className="movie-poster">Capa</div>

                                    <div className="movie-info">
                                        <h3>titulo do filme</h3>
                                        <p className="movie-year">ano do filme</p>

                                        <ul className="movie-genres" aria-label="Gêneros">
                                            <li>genero1</li>
                                            <li>genero2</li>
                                        </ul>

                                    </div>

                                    <div className="movie-actions">
                                        <button
                                            type="button"
                                            aria-label="Remover dos favoritos"
                                            aria-pressed={true}
                                        >
                                            ♥
                                        </button>

                                        <button
                                            type="button"
                                            aria-label="Mais opções"
                                        >
                                            ⋮
                                        </button>
                                    </div>
                                </article>
                            </li>
                        </ul>
                    </section>
                </div>
            </main>
        </div>
        </>
    );
}