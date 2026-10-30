import Header from "../components/Header.jsx";
import "./Games.css";

export default function Games() {
    return (
        <>
            <Header />

            <div className="games-page">
                <main className="games-content">
                    <section className="games-heading" aria-labelledby="games-title">
                        <div>
                            <h1 id="games-title">🎮 Meus jogos</h1>
                            <p>Acompanhe sua jornada pelos mundos que mais gosta.</p>
                        </div>

                        <button className="add-game-button" type="button">
                            + Adicionar jogo
                        </button>
                    </section>

                    <div className="games-columns">
                        {/* Quero jogar */}
                        <section className="game-column" aria-labelledby="wishlist-title">
                            <header className="game-column-header">
                                <h2 id="wishlist-title">
                                    <span className="game-status-dot game-status-pending" />
                                    Quero jogar
                                </h2>

                                <span className="game-count">1</span>
                            </header>

                            <ul className="game-list">
                                <li>
                                    <article className="game-card">
                                        <div className="game-cover">Capa</div>

                                        <div className="game-info">
                                            <h3>Elden Ring</h3>
                                            <p className="game-platforms">PC · PS5 · Xbox</p>

                                            <ul className="game-genres" aria-label="Gêneros">
                                                <li>RPG</li>
                                                <li>Ação</li>
                                            </ul>
                                        </div>

                                        <div className="game-actions">
                                            <button
                                                type="button"
                                                aria-label="Favoritar Elden Ring"
                                                aria-pressed={false}
                                            >
                                                ♡
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para Elden Ring"
                                            >
                                                ⋮
                                            </button>
                                        </div>
                                    </article>
                                </li>
                            </ul>
                        </section>

                        {/* Jogando */}
                        <section className="game-column" aria-labelledby="playing-title">
                            <header className="game-column-header">
                                <h2 id="playing-title">
                                    <span className="game-status-dot game-status-playing" />
                                    Jogando
                                </h2>

                                <span className="game-count">1</span>
                            </header>

                            <ul className="game-list">
                                <li>
                                    <article className="game-card">
                                        <div className="game-cover">Capa</div>

                                        <div className="game-info">
                                            <h3>Hades</h3>
                                            <p className="game-platforms">PC · Switch</p>

                                            <ul className="game-genres" aria-label="Gêneros">
                                                <li>Roguelike</li>
                                                <li>Ação</li>
                                            </ul>
                                        </div>

                                        <div className="game-actions">
                                            <button
                                                type="button"
                                                aria-label="Remover Hades dos favoritos"
                                                aria-pressed={true}
                                            >
                                                ♥
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para Hades"
                                            >
                                                ⋮
                                            </button>
                                        </div>
                                    </article>
                                </li>
                            </ul>
                        </section>

                        {/* Concluídos */}
                        <section className="game-column" aria-labelledby="completed-title">
                            <header className="game-column-header">
                                <h2 id="completed-title">
                                    <span className="game-status-dot game-status-completed" />
                                    Concluídos
                                </h2>

                                <span className="game-count">1</span>
                            </header>

                            <ul className="game-list">
                                <li>
                                    <article className="game-card">
                                        <div className="game-cover">Capa</div>

                                        <div className="game-info">
                                            <h3>Hollow Knight</h3>
                                            <p className="game-platforms">PC · Switch</p>

                                            <ul className="game-genres" aria-label="Gêneros">
                                                <li>Ação</li>
                                                <li>Metroidvania</li>
                                            </ul>

                                            <p className="game-rating" aria-label="5 de 5 estrelas">
                                                <span aria-hidden="true">★★★★★</span>
                                            </p>
                                        </div>

                                        <div className="game-actions">
                                            <button
                                                type="button"
                                                aria-label="Favoritar Hollow Knight"
                                                aria-pressed={false}
                                            >
                                                ♡
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para Hollow Knight"
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