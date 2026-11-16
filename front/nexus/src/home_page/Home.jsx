import FavoriteButton from "../Components/FavoriteButton.jsx";
import "./Home.css";
import Header from "../Components/Header.jsx";
import { Link, useOutletContext } from "react-router-dom";
import useLibrary from "../hooks/useLibrary";

function Home() {
  const context = useOutletContext();
  const user = context?.user;

  const {
    library,
    reloadLibrary,
    fullContent,
    libraryError,
    loadingLibrary,
  } = useLibrary(user?.id);

  if (!user) {
    return <p>Dados do usuário não foram recebidos.</p>;
  }

  if (user.id == null) {
    return <p>A resposta do usuário não contém um ID.</p>;
  }

  if (loadingLibrary) {
    return <p>Carregando biblioteca...</p>;
  }

  if (libraryError) {
    return <p role="alert">{libraryError}</p>;
  }

  const catalog = new Map(fullContent.map((item) => [String(item._id), item]));
  const favorites = library.filter((row) => row[9] === true).flatMap((row) => {
    const item = catalog.get(String(row[2]));
    return item ? [{ ...item, registroId: row[0] }] : [];
  });
  const contentRoutes = { movie: "/filmes", game: "/jogos", book: "/livros" };
  const contentLabels = { movie: "Filme", game: "Jogo", book: "Livro" };

  return (
      <>
        <Header />

        <main className="home">
          <section className="hero" aria-labelledby="hero-title">
            <h1 id="hero-title">Sua próxima história começa aqui.</h1>
            <p>Filmes, jogos e livros. Tudo no seu ritmo.</p>
          </section>

          <div className="dashboard-grid">
            <section className="panel" aria-labelledby="watching-title">
              <header className="panel-header">
                <h2 id="watching-title">Acompanhando agora</h2>
              </header>

              {fullContent.length === 0 ? (
                  <p>Sua biblioteca ainda está vazia.</p>
              ) : (
                  <ul className="cards-grid">
                    {fullContent.slice(0, 3).map((item) => (
                        <li key={item._id}>
                          <article className="media-card">
                            <div className="cover-wrapper">
                              <a href="#" aria-label="Ver detalhes">
                                <img
                                    src={item.poster}
                                    height={200}
                                    alt="Capa"
                                />
                              </a>
                            </div>

                            <p className="lancamento">
                              {item.type} · {item.date}
                            </p>

                            <ul className="tags" aria-label="Gêneros">
                              {(item.genres ?? [])
                                  .slice(0, 3)
                                  .map((genre, index) => (
                                      <li key={`${genre}-${index}`}>
                                        {genre}
                                      </li>
                                  ))}
                            </ul>
                          </article>
                        </li>
                    ))}
                  </ul>
              )}
            </section>

            <section className="panel" aria-labelledby="favorites-title">
              <header className="panel-header">
                <h2 id="favorites-title">Seus favoritos</h2>
              </header>

              {favorites.length === 0 ? (
                <p>Seus favoritos aparecem aqui. Toque no coração de um filme, jogo ou livro.</p>
              ) : (
                <ul className="cards-grid favorites-scroll" tabIndex={0} aria-labelledby="favorites-title">
                  {favorites.map((item) => (
                    <li key={item.registroId}>
                      <article className="media-card">
                        <div className="cover-wrapper favorite-cover">
                          <Link to={contentRoutes[item.type] ?? "/"} aria-label={"Ver " + item.title}>
                            {(item.poster ?? item.img_url) ? <img src={item.poster ?? item.img_url} alt={"Capa de " + item.title} /> : <span className="favorite-placeholder">Sem capa</span>}
                          </Link>
                          <FavoriteButton id={item.registroId} title={item.title} favorite={true} onChanged={reloadLibrary} />
                        </div>
                        <h3><Link to={contentRoutes[item.type] ?? "/"}>{item.title}</Link></h3>
                        <p>{contentLabels[item.type] ?? item.type}</p>
                      </article>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>

          {/*<section className="panel recent" aria-labelledby="recent-title">*/}
          {/*  <header className="panel-header">*/}
          {/*    <h2 id="recent-title">Adicionados recentemente</h2>*/}

          {/*    <Link to="/recentes">*/}
          {/*      Ver todos <span aria-hidden="true">→</span>*/}
          {/*    </Link>*/}
          {/*  </header>*/}

          {/*  <ul className="recent-grid"></ul>*/}
          {/*</section>*/}
        </main>
      </>
  );
}

export default Home;