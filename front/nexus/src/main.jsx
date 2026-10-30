import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Home from './home_page/Home.jsx'
import Movies from './movies_page/Movies.jsx'
import Games from './games_page/Games.jsx'
import Books from './books_page/Books.jsx'
import Login from "./login_page/Login.jsx";
import Register from "./register_page/Register.jsx"
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { BrowserRouter, Routes, Route } from "react-router-dom";

createRoot(document.getElementById('root')).render(
  <StrictMode>
      <BrowserRouter>
          <Routes>

              <Route path="/login" element={<Login />} />
              <Route path="/cadastro" element={<Register />} />
              <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Home />} />
              <Route path="/filmes" element={<Movies />} />
              <Route path="/jogos" element={<Games />} />
              <Route path="/livros" element={<Books />} />
              </Route>
          </Routes>
      </BrowserRouter>
  </StrictMode>,
)
