import "./Home.css"
import Header from "../Components/Header.jsx"
import Movies from "../movies_page/Movies.jsx"
import user_icon from "../assets/user_icon.png";
import claquete from "../assets/claquete-roxa.png";
import controle from "../assets/controle-azul.png";
import livro from "../assets/livro-vermelho.png";
import casinha from "../assets/casinha-verde.png";
import bttf from "../assets/bttf.jpg";
import { Link, useOutletContext } from "react-router-dom";
import {useEffect, useState} from "react";



function Home() {
  const context = useOutletContext();
  const user = context?.user;
  const id = user?.id;

  const [library, setLibrary] = useState(null);
  const [libraryError, setLibraryError] = useState("");
  const [loadingLibrary, setLoadingLibrary] = useState(true);

  useEffect(() => {
    if (id == null) return;

    const controller = new AbortController();

    async function getLibrary() {
      setLoadingLibrary(true);
      setLibraryError("");

      try {
        // Ajuste o parâmetro conforme a definição da sua API.
        const response = await fetch(
            `http://localhost:8000/library`,
            {
              method: "GET",
              credentials: "include",
              signal: controller.signal,
            }
        );

        if (!response.ok) {
          throw new Error(
              `Não foi possível buscar a biblioteca (${response.status}).`
          );
        }

        const data = await response.json();
        console.log(data);
        if (!controller.signal.aborted) {
          setLibrary(data);
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          setLibraryError(error.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoadingLibrary(false);
        }
      }
    }

    getLibrary();

    return () => controller.abort();
  }, [id]);

  if (!user) {
    return <p>Dados do usuário não foram recebidos.</p>;
  }

  if (id == null) {
    return <p>A resposta do usuário não contém um ID.</p>;
  }

  if (loadingLibrary) {
    return <p>Carregando biblioteca...</p>;
  }

  if (libraryError) {
    return <p role="alert">{libraryError}</p>;
  }




  return (
      <>
      <Header />


      <main className="home">
        <section className="hero" aria-labelledby="hero-title">
          <h1 id="hero-title">Sua próxima história começa aqui.</h1>
          <p>Filmes, jogos e livros. Tudo no seu ritmo.</p>
        </section>

        <section className="collection-summary" aria-labelledby="summary-title">
          <h2 id="summary-title" className="sr-only">Resumo do acervo</h2>

          <ul className="summary-grid">
            <li><a className="bloco" href="/filmes">
              <img src={claquete} width="30" height="30" alt="claquete"/>
              Filmes <strong>28</strong></a></li>

            <li><a className="bloco" href="/jogos">
              <img src={controle} width="30" height="30" alt="claquete"/>
              Jogos <strong>16</strong></a></li>

            <li><a className="bloco" href="/livros">
              <img src={livro} width="30" height="30" alt="claquete"/>
              Livros <strong>24</strong></a></li>

          </ul>
        </section>

        <div className="dashboard-grid">
          <section className="panel" aria-labelledby="watching-title">
            <header className="panel-header">
              <h2 id="watching-title">Acompanhando agora</h2>
              <a href="/acompanhando">Ver todos <span aria-hidden="true">→</span></a>
            </header>


            {/*ACOMPANHANDO*/}
            <ul className="cards-grid">
              <li>
                <article className="media-card">
                  <div className="cover-wrapper">
                    <a href="#" aria-label="Ver detalhes de Duna">
                      <img src={bttf} alt="Capa"/>
                    </a>

                  </div>

                  <h3><a href="#">Filme</a></h3>
                  <p>Filme · <time dateTime="ano">Data</time></p>

                  <ul className="tags" aria-label="Gêneros">
                    <li>genero1</li>
                    <li>genero2</li>
                  </ul>
                </article>
              </li>

              <li>
                <article className="media-card">
                  <div className="cover-wrapper">
                    <a href="#" aria-label="Ver detalhes de Duna">
                      <img src={bttf} alt="Capa"/>
                    </a>

                  </div>

                  <h3><a href="#">Filme</a></h3>
                  <p>Filme · <time dateTime="ano">Data</time></p>

                  <ul className="tags" aria-label="Gêneros">
                    <li>genero1</li>
                    <li>genero2</li>
                  </ul>
                </article>
              </li>

              <li>
                <article className="media-card">
                  <div className="cover-wrapper">
                    <a href="#" aria-label="Ver detalhes de Duna">
                      <img src={bttf} alt="Capa"/>
                    </a>

                  </div>

                  <h3><a href="#">Filme</a></h3>
                  <p>Filme · <time dateTime="ano">Data</time></p>

                  <ul className="tags" aria-label="Gêneros">
                    <li>genero1</li>
                    <li>genero2</li>
                  </ul>
                </article>
              </li>


            </ul>
          </section>

          <section className="panel" aria-labelledby="favorites-title">
            <header className="panel-header">
              <h2 id="favorites-title">Seus favoritos</h2>
              <a href="/favoritos">Ver todos <span aria-hidden="true">→</span></a>
            </header>

            <ul className="cards-grid">

            </ul>
          </section>
        </div>

        <section className="panel recent" aria-labelledby="recent-title">
          <header className="panel-header">
            <h2 id="recent-title">Adicionados recentemente</h2>
            <a href="/recentes">Ver todos <span aria-hidden="true">→</span></a>
          </header>

          <ul className="recent-grid">

          </ul>
        </section>
      </main>

      </>
  )
}

export default Home
