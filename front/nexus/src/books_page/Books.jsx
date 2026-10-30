import Header from "../components/Header.jsx";
import "./Books.css";

export default function Books() {
    return (
        <>
            <Header />

            <div className="books-page">
                <main className="books-content">
                    <section className="books-heading" aria-labelledby="books-title">
                        <div>
                            <h1 id="books-title">📖 Meus livros</h1>
                            <p>Descubra novas leituras e acompanhe seu progresso.</p>
                        </div>

                        <button className="add-book-button" type="button">
                            + Adicionar livro
                        </button>
                    </section>

                    <div className="books-columns">
                        {/* Quero ler */}
                        <section className="book-column" aria-labelledby="to-read-title">
                            <header className="book-column-header">
                                <h2 id="to-read-title">
                                    <span className="book-status-dot book-status-pending" />
                                    Quero ler
                                </h2>

                                <span className="book-count">1</span>
                            </header>

                            <ul className="book-list">
                                <li>
                                    <article className="book-card">
                                        <div className="book-cover">Capa</div>

                                        <div className="book-info">
                                            <h3>Duna</h3>
                                            <p className="book-author">Frank Herbert</p>

                                            <ul className="book-genres" aria-label="Gêneros">
                                                <li>Ficção científica</li>
                                                <li>Clássico</li>
                                            </ul>
                                        </div>

                                        <div className="book-actions">
                                            <button
                                                type="button"
                                                aria-label="Favoritar Duna"
                                                aria-pressed={false}
                                            >
                                                ♡
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para Duna"
                                            >
                                                ⋮
                                            </button>
                                        </div>
                                    </article>
                                </li>
                            </ul>
                        </section>

                        {/* Lendo */}
                        <section className="book-column" aria-labelledby="reading-title">
                            <header className="book-column-header">
                                <h2 id="reading-title">
                                    <span className="book-status-dot book-status-reading" />
                                    Lendo
                                </h2>

                                <span className="book-count">1</span>
                            </header>

                            <ul className="book-list">
                                <li>
                                    <article className="book-card">
                                        <div className="book-cover">Capa</div>

                                        <div className="book-info">
                                            <h3>O Hobbit</h3>
                                            <p className="book-author">J.R.R. Tolkien</p>

                                            <ul className="book-genres" aria-label="Gêneros">
                                                <li>Fantasia</li>
                                                <li>Aventura</li>
                                            </ul>
                                        </div>

                                        <div className="book-actions">
                                            <button
                                                type="button"
                                                aria-label="Remover O Hobbit dos favoritos"
                                                aria-pressed={true}
                                            >
                                                ♥
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para O Hobbit"
                                            >
                                                ⋮
                                            </button>
                                        </div>
                                    </article>
                                </li>
                            </ul>
                        </section>

                        {/* Lidos */}
                        <section className="book-column" aria-labelledby="read-title">
                            <header className="book-column-header">
                                <h2 id="read-title">
                                    <span className="book-status-dot book-status-read" />
                                    Lidos
                                </h2>

                                <span className="book-count">1</span>
                            </header>

                            <ul className="book-list">
                                <li>
                                    <article className="book-card">
                                        <div className="book-cover">Capa</div>

                                        <div className="book-info">
                                            <h3>O Senhor dos Anéis</h3>
                                            <p className="book-author">J.R.R. Tolkien</p>

                                            <ul className="book-genres" aria-label="Gêneros">
                                                <li>Fantasia</li>
                                                <li>Aventura</li>
                                            </ul>

                                            <p className="book-rating" aria-label="5 de 5 estrelas">
                                                <span aria-hidden="true">★★★★★</span>
                                            </p>
                                        </div>

                                        <div className="book-actions">
                                            <button
                                                type="button"
                                                aria-label="Remover O Senhor dos Anéis dos favoritos"
                                                aria-pressed={true}
                                            >
                                                ♥
                                            </button>

                                            <button
                                                type="button"
                                                aria-label="Mais opções para O Senhor dos Anéis"
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