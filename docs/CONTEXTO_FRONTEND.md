# 📱 Contexto para Desarrollo de Frontend - Contratos e Informes

## 🎯 Objetivo

Este documento proporciona todo el contexto necesario para construir un frontend que permita a los usuarios:
1. **Autenticarse** con sus credenciales de Bonita
2. **Visualizar sus contratos** asociados a su perfil
3. **Seleccionar un contrato** y ver sus informes asociados

---

## 🏗️ Arquitectura y Flujo

```
┌─────────────────┐
│   Frontend      │
│  (Vue/React)   │
└────────┬────────┘
         │
         │ HTTP/REST + JWT
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│  (Backend)      │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────┐  ┌──────────────┐
│   Bonita    │  │  PostgreSQL  │
│  (Auth)     │  │  (BDM Data)  │
└─────────────┘  └──────────────┘
```

### Flujo de Autenticación

1. Usuario ingresa **username** y **password** (credenciales de Bonita)
2. Frontend envía credenciales a `/api/auth/token`
3. Backend valida con Bonita y retorna **JWT token**
4. Frontend almacena el token y lo incluye en todas las peticiones siguientes

### Flujo de Datos

1. Usuario autenticado → Frontend obtiene `username` del JWT
2. Frontend necesita obtener el `id_usuario_bonita` del perfil del usuario
3. Con `id_usuario_bonita` → Frontend consulta contratos del usuario
4. Al seleccionar un contrato → Frontend consulta informes de ese contrato

---

## 🔐 Autenticación

### Endpoint: Obtener Token JWT

**POST** `/api/auth/token`

**Content-Type:** `application/x-www-form-urlencoded`

**Body:**
```
username=walter.bates
password=bpm
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Credenciales de Bonita inválidas."
}
```

### Uso del Token

Todas las peticiones a endpoints protegidos deben incluir el header:

```
Authorization: Bearer {access_token}
```

### Información del Token

El JWT contiene:
- `sub`: Username del usuario (ej: "walter.bates")
- `exp`: Fecha de expiración (por defecto 30 minutos)

**⚠️ Importante:** El token NO contiene el `id_usuario_bonita`. Necesitas obtenerlo del perfil del usuario.

---

## 📊 Endpoints Principales

### Base URL

```
http://localhost:8000/api
```

### 1. Obtener Perfil del Usuario

**GET** `/api/bdm/perfiles-contratista/por-usuario-bonita/{id_usuario_bonita}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "00000000-0000-0000-0000-000000005001",
  "nombre_completo": "Juan Carlos Pérez López",
  "documento_identidad": "1234567890",
  "id_usuario_bonita": "5001",
  "estado": 1
}
```

**Nota:** Necesitas mapear el `username` del JWT al `id_usuario_bonita`. Esto puede requerir un endpoint adicional o una tabla de mapeo.

### 2. Listar Contratos del Usuario

**GET** `/api/bdm/contratos/usuario/{id_usuario_bonita}?skip=0&limit=100`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `skip` (int, default: 0): Número de registros a saltar (paginación)
- `limit` (int, default: 100, max: 1000): Número máximo de registros

**Response (200 OK):**
```json
[
  {
    "id": "00000000-0000-0000-0000-000000004001",
    "numero_contrato": "CONT-2024-0015",
    "fecha_inicio": "2024-10-01",
    "estado": "Activo",
    "plazo": "12 meses",
    "objeto": "Prestación de servicios de desarrollo...",
    "valor_contrato": 150000000.00,
    "supervisor": 1002,
    "perfil_contratista_id": "00000000-0000-0000-0000-000000005001",
    "padre_id": "00000000-0000-0000-0000-000000000002"
  }
]
```

### 3. Obtener Contrato Completo (con relaciones)

**GET** `/api/bdm/contratos/{contrato_id}/completo`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "00000000-0000-0000-0000-000000004001",
  "numero_contrato": "CONT-2024-0015",
  "fecha_inicio": "2024-10-01",
  "estado": "Activo",
  "plazo": "12 meses",
  "objeto": "Prestación de servicios...",
  "valor_contrato": 150000000.00,
  "supervisor": 1002,
  "perfil_contratista_id": "00000000-0000-0000-0000-000000005001",
  "padre_id": "00000000-0000-0000-0000-000000000002",
  "perfil_contratista": {
    "id": "00000000-0000-0000-0000-000000005001",
    "nombre_completo": "Juan Carlos Pérez López",
    "documento_identidad": "1234567890",
    "id_usuario_bonita": "5001",
    "estado": 1
  },
  "informes": [
    {
      "id": "00000000-0000-0000-0000-000000005001",
      "valor_periodo": 12500000.00,
      "estado": "Aprobado",
      "mes": 10,
      "anio": 2024,
      "fecha_inicio_periodo": "2024-10-01",
      "fecha_fin_periodo": "2024-10-31",
      "contrato_id": "00000000-0000-0000-0000-000000004001"
    }
  ],
  "obligaciones": [
    {
      "id": "00000000-0000-0000-0000-000000000401",
      "indice": 1,
      "descripcion": "Entregar informes mensuales de avance",
      "contrato_id": "00000000-0000-0000-0000-000000004001"
    }
  ]
}
```

### 4. Listar Informes de un Contrato

**GET** `/api/bdm/informes/contrato/{contrato_id}?skip=0&limit=100`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "00000000-0000-0000-0000-000000005001",
    "valor_periodo": 12500000.00,
    "estado": "Aprobado",
    "mes": 10,
    "anio": 2024,
    "fecha_inicio_periodo": "2024-10-01",
    "fecha_fin_periodo": "2024-10-31",
    "contrato_id": "00000000-0000-0000-0000-000000004001"
  },
  {
    "id": "00000000-0000-0000-0000-000000005002",
    "valor_periodo": 12500000.00,
    "estado": "En Revisión",
    "mes": 11,
    "anio": 2024,
    "fecha_inicio_periodo": "2024-11-01",
    "fecha_fin_periodo": "2024-11-30",
    "contrato_id": "00000000-0000-0000-0000-000000004001"
  }
]
```

### 5. Obtener Informe Completo (con ejecuciones)

**GET** `/api/bdm/informes/{informe_id}/completo`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "00000000-0000-0000-0000-000000005001",
  "valor_periodo": 12500000.00,
  "estado": "Aprobado",
  "mes": 10,
  "anio": 2024,
  "fecha_inicio_periodo": "2024-10-01",
  "fecha_fin_periodo": "2024-10-31",
  "contrato_id": "00000000-0000-0000-0000-000000004001",
  "ejecuciones": [
    {
      "id": "00000000-0000-0000-0000-000000006001",
      "evidencia_adjunta": "informe_octubre_2024.pdf",
      "obligacion_id": "00000000-0000-0000-0000-000000000401",
      "informe_id": "00000000-0000-0000-0000-000000005001"
    }
  ]
}
```

---

## 📋 Estructura de Datos

### Contrato

```typescript
interface Contrato {
  id: string;                    // UUID
  numero_contrato?: string;
  fecha_inicio?: string;         // ISO date: "2024-10-01"
  estado?: string;               // "Activo", "Finalizado", etc.
  plazo?: string;                // "12 meses"
  objeto?: string;               // Descripción del contrato
  valor_contrato?: number;       // Decimal
  supervisor?: number;           // BigInteger
  perfil_contratista_id: string; // UUID (requerido)
  padre_id: string;              // UUID (requerido)
}
```

### Contrato con Relaciones

```typescript
interface ContratoCompleto extends Contrato {
  perfil_contratista?: PerfilContratista;
  informes: Informe[];
  obligaciones: Obligacion[];
}
```

### Informe

```typescript
interface Informe {
  id: string;                    // UUID
  valor_periodo?: number;         // Decimal
  estado?: string;               // "Aprobado", "En Revisión", "Pendiente"
  mes?: number;                  // 1-12
  anio?: number;                 // 2024
  fecha_inicio_periodo?: string;  // ISO date
  fecha_fin_periodo?: string;     // ISO date
  contrato_id?: string;          // UUID
}
```

### PerfilContratista

```typescript
interface PerfilContratista {
  id: string;                    // UUID
  nombre_completo?: string;
  documento_identidad?: string;
  id_usuario_bonita?: string;    // ⚠️ Importante para filtrar contratos
  estado?: number;
}
```

---

## 🔄 Flujo de Navegación del Frontend

### 1. Página de Login

```
┌─────────────────────────┐
│   Login                 │
│                         │
│   Username: [_______]   │
│   Password: [_______]   │
│                         │
│   [Iniciar Sesión]      │
└─────────────────────────┘
         │
         │ POST /api/auth/token
         ▼
    ┌─────────┐
    │  JWT    │
    │  Token  │
    └─────────┘
```

### 2. Página de Lista de Contratos

```
┌─────────────────────────────────────┐
│  Mis Contratos                      │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ CONT-2024-0015                │ │
│  │ Estado: Activo                │ │
│  │ Valor: $150,000,000           │ │
│  │ Fecha: 2024-10-01             │ │
│  │ [Ver Detalles]                │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ CONT-2024-0016                │ │
│  │ Estado: Finalizado            │ │
│  │ ...                           │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 3. Página de Detalle de Contrato

```
┌─────────────────────────────────────┐
│  Contrato: CONT-2024-0015           │
│                                     │
│  Información General:               │
│  - Estado: Activo                   │
│  - Valor: $150,000,000              │
│  - Fecha Inicio: 2024-10-01         │
│                                     │
│  Informes:                          │
│  ┌───────────────────────────────┐ │
│  │ Octubre 2024                   │ │
│  │ Estado: Aprobado               │ │
│  │ Valor: $12,500,000             │ │
│  │ [Ver Detalles]                 │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Noviembre 2024                 │ │
│  │ Estado: En Revisión            │ │
│  │ ...                            │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 4. Página de Detalle de Informe

```
┌─────────────────────────────────────┐
│  Informe - Octubre 2024             │
│                                     │
│  Período: 2024-10-01 a 2024-10-31  │
│  Estado: Aprobado                   │
│  Valor: $12,500,000                 │
│                                     │
│  Ejecuciones:                       │
│  - Informe entregado                │
│  - Actas de reuniones               │
│  - Pruebas de calidad               │
└─────────────────────────────────────┘
```

---

## 💻 Ejemplos de Código

### JavaScript/TypeScript - Cliente API

```typescript
// api/client.ts
const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  private token: string | null = null;

  // Autenticación
  async login(username: string, password: string): Promise<string> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Credenciales inválidas');
    }

    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('access_token', this.token);
    return this.token;
  }

  // Obtener token almacenado
  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('access_token');
    }
    return this.token;
  }

  // Headers con autenticación
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // Obtener perfil por id_usuario_bonita
  async getPerfilByUsuarioBonita(idUsuarioBonita: string) {
    const response = await fetch(
      `${API_BASE_URL}/bdm/perfiles-contratista/por-usuario-bonita/${idUsuarioBonita}`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener perfil');
    }

    return response.json();
  }

  // Listar contratos del usuario
  async getContratosByUsuario(idUsuarioBonita: string, skip = 0, limit = 100) {
    const response = await fetch(
      `${API_BASE_URL}/bdm/contratos/usuario/${idUsuarioBonita}?skip=${skip}&limit=${limit}`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener contratos');
    }

    return response.json();
  }

  // Obtener contrato completo
  async getContratoCompleto(contratoId: string) {
    const response = await fetch(
      `${API_BASE_URL}/bdm/contratos/${contratoId}/completo`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener contrato');
    }

    return response.json();
  }

  // Listar informes de un contrato
  async getInformesByContrato(contratoId: string, skip = 0, limit = 100) {
    const response = await fetch(
      `${API_BASE_URL}/bdm/informes/contrato/${contratoId}?skip=${skip}&limit=${limit}`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener informes');
    }

    return response.json();
  }

  // Obtener informe completo
  async getInformeCompleto(informeId: string) {
    const response = await fetch(
      `${API_BASE_URL}/bdm/informes/${informeId}/completo`,
      {
        headers: this.getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Error al obtener informe');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
```

### React - Hook de Autenticación

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface User {
  username: string;
  idUsuarioBonita?: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay token almacenado
    const token = apiClient.getToken();
    if (token) {
      // Decodificar JWT para obtener username
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({ username: payload.sub });
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const token = await apiClient.login(username, password);
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({ username: payload.sub });
      return true;
    } catch (error) {
      console.error('Error de autenticación:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return { user, loading, login, logout };
}
```

### React - Componente de Lista de Contratos

```typescript
// components/ContratosList.tsx
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAuth } from '../hooks/useAuth';

interface Contrato {
  id: string;
  numero_contrato?: string;
  estado?: string;
  valor_contrato?: number;
  fecha_inicio?: string;
}

export function ContratosList() {
  const { user } = useAuth();
  const [contratos, setContratos] = useState<Contrato[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadContratos = async () => {
      if (!user) return;

      try {
        setLoading(true);
        // ⚠️ Necesitas obtener id_usuario_bonita del perfil
        // Por ahora asumimos que lo tienes mapeado
        const idUsuarioBonita = '5001'; // TODO: Obtener del perfil
        
        const data = await apiClient.getContratosByUsuario(idUsuarioBonita);
        setContratos(data);
      } catch (err) {
        setError('Error al cargar contratos');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadContratos();
  }, [user]);

  if (loading) return <div>Cargando contratos...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Mis Contratos</h2>
      {contratos.length === 0 ? (
        <p>No tienes contratos asignados</p>
      ) : (
        <ul>
          {contratos.map((contrato) => (
            <li key={contrato.id}>
              <h3>{contrato.numero_contrato || 'Sin número'}</h3>
              <p>Estado: {contrato.estado}</p>
              <p>Valor: ${contrato.valor_contrato?.toLocaleString()}</p>
              <a href={`/contratos/${contrato.id}`}>Ver Detalles</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### React - Componente de Detalle de Contrato

```typescript
// components/ContratoDetail.tsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '../api/client';

interface Informe {
  id: string;
  mes?: number;
  anio?: number;
  estado?: string;
  valor_periodo?: number;
}

export function ContratoDetail() {
  const { contratoId } = useParams<{ contratoId: string }>();
  const [contrato, setContrato] = useState<any>(null);
  const [informes, setInformes] = useState<Informe[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      if (!contratoId) return;

      try {
        setLoading(true);
        
        // Opción 1: Obtener contrato completo (incluye informes)
        const contratoCompleto = await apiClient.getContratoCompleto(contratoId);
        setContrato(contratoCompleto);
        setInformes(contratoCompleto.informes || []);

        // Opción 2: Obtener informes por separado
        // const informesData = await apiClient.getInformesByContrato(contratoId);
        // setInformes(informesData);
      } catch (error) {
        console.error('Error al cargar datos:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [contratoId]);

  if (loading) return <div>Cargando...</div>;
  if (!contrato) return <div>Contrato no encontrado</div>;

  const getMesNombre = (mes?: number) => {
    const meses = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return meses[(mes || 1) - 1];
  };

  return (
    <div>
      <h2>Contrato: {contrato.numero_contrato}</h2>
      <div>
        <p><strong>Estado:</strong> {contrato.estado}</p>
        <p><strong>Valor:</strong> ${contrato.valor_contrato?.toLocaleString()}</p>
        <p><strong>Fecha Inicio:</strong> {contrato.fecha_inicio}</p>
      </div>

      <h3>Informes</h3>
      {informes.length === 0 ? (
        <p>No hay informes para este contrato</p>
      ) : (
        <ul>
          {informes.map((informe) => (
            <li key={informe.id}>
              <h4>
                {getMesNombre(informe.mes)} {informe.anio}
              </h4>
              <p>Estado: {informe.estado}</p>
              <p>Valor: ${informe.valor_periodo?.toLocaleString()}</p>
              <a href={`/informes/${informe.id}`}>Ver Detalles</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## ⚠️ Consideraciones Importantes

### 1. Mapeo Username → id_usuario_bonita

El JWT solo contiene el `username` (ej: "walter.bates"), pero para obtener los contratos necesitas el `id_usuario_bonita` (ej: "5001").

**Opciones:**

**Opción A:** Crear un endpoint que retorne el perfil basado en el username del JWT:
```typescript
// Endpoint sugerido (puede requerir implementación en backend)
GET /api/bdm/perfiles-contratista/por-username/{username}
```

**Opción B:** Almacenar el mapeo en el frontend después de la primera consulta:
```typescript
// Después de login, buscar el perfil
const perfiles = await apiClient.getPerfiles();
const perfil = perfiles.find(p => p.id_usuario_bonita === username);
// Almacenar id_usuario_bonita en localStorage
```

**Opción C:** Modificar el backend para que el endpoint de contratos acepte username y haga el mapeo internamente.

### 2. Manejo de Errores

```typescript
// Manejo de errores HTTP
try {
  const data = await apiClient.getContratosByUsuario(idUsuarioBonita);
} catch (error) {
  if (error instanceof Response) {
    if (error.status === 401) {
      // Token expirado o inválido
      // Redirigir a login
    } else if (error.status === 404) {
      // Recurso no encontrado
    } else if (error.status >= 500) {
      // Error del servidor
    }
  }
}
```

### 3. Expiración del Token

El token expira después de 30 minutos (configurable). Implementa:

```typescript
// Verificar expiración antes de cada petición
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convertir a milisegundos
    return Date.now() >= exp;
  } catch {
    return true;
  }
}

// Interceptor para renovar token
if (isTokenExpired(token)) {
  // Redirigir a login o renovar token
}
```

### 4. Paginación

Los endpoints soportan paginación con `skip` y `limit`:

```typescript
// Implementar paginación
const [page, setPage] = useState(0);
const pageSize = 10;

const loadContratos = async () => {
  const data = await apiClient.getContratosByUsuario(
    idUsuarioBonita,
    page * pageSize,
    pageSize
  );
};
```

---

## 🧪 Testing

### Variables de Entorno

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Datos de Prueba

Usa los UUIDs del script SQL de datos de prueba:
- `contrato_id`: `00000000-0000-0000-0000-000000004001`
- `informe_id`: `00000000-0000-0000-0000-000000005001`
- `id_usuario_bonita`: `5001`

---

## 📚 Recursos Adicionales

- **Colección Postman:** `docs/PythonBonitaDemo - Contratos e Informes.postman_collection.json`
- **Script SQL de Datos:** `scripts/gestorContratos_datos_postgresql.sql`
- **Documentación API:** Ejecutar FastAPI y visitar `http://localhost:8000/docs`

---

## ✅ Checklist de Implementación

- [ ] Configurar cliente HTTP con base URL
- [ ] Implementar autenticación (login/logout)
- [ ] Almacenar y manejar JWT token
- [ ] Implementar mapeo username → id_usuario_bonita
- [ ] Crear componente de lista de contratos
- [ ] Crear componente de detalle de contrato
- [ ] Crear componente de lista de informes
- [ ] Crear componente de detalle de informe
- [ ] Implementar manejo de errores
- [ ] Implementar loading states
- [ ] Implementar paginación (si es necesario)
- [ ] Implementar renovación de token
- [ ] Testing con datos reales

---

**Última actualización:** 2024-12-XX

