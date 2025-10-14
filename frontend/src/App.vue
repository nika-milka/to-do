<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <span class="navbar-brand">✅ Taskly</span>
        <div v-if="isAuthenticated" class="navbar-nav ms-auto">
          <span class="navbar-text me-3">
            Привет, <strong>{{ currentUser }}</strong>!
          </span>
          <button class="btn btn-outline-light btn-sm" @click="logout">
            Выйти
          </button>
        </div>
      </div>
    </nav>

    <main class="container mt-4">
      <!-- Страница входа/регистрации -->
      <div v-if="!isAuthenticated">
        <div class="row justify-content-center">
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <ul class="nav nav-tabs card-header-tabs">
                  <li class="nav-item">
                    <button 
                      class="nav-link" 
                      :class="{ active: activeTab === 'login' }"
                      @click="activeTab = 'login'"
                    >
                      Вход
                    </button>
                  </li>
                  <li class="nav-item">
                    <button 
                      class="nav-link" 
                      :class="{ active: activeTab === 'register' }"
                      @click="activeTab = 'register'"
                    >
                      Регистрация
                    </button>
                  </li>
                </ul>
              </div>
              
              <div class="card-body">
                <!-- Форма входа -->
                <div v-if="activeTab === 'login'">
                  <div class="mb-3">
                    <label class="form-label">Имя пользователя</label>
                    <input 
                      v-model="loginData.username" 
                      type="text" 
                      class="form-control"
                      placeholder="Введите имя пользователя"
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Пароль</label>
                    <input 
                      v-model="loginData.password" 
                      type="password" 
                      class="form-control"
                      placeholder="Введите пароль"
                    >
                  </div>
                  <button 
                    @click="login" 
                    class="btn btn-primary w-100"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Вход...' : 'Войти' }}
                  </button>
                </div>
                
                <!-- Форма регистрации -->
                <div v-if="activeTab === 'register'">
                  <div class="mb-3">
                    <label class="form-label">Имя пользователя</label>
                    <input 
                      v-model="registerData.username" 
                      type="text" 
                      class="form-control"
                      placeholder="Придумайте имя пользователя"
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Пароль</label>
                    <input 
                      v-model="registerData.password" 
                      type="password" 
                      class="form-control"
                      placeholder="Придумайте пароль (минимум 6 символов)"
                    >
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Подтверждение пароля</label>
                    <input 
                      v-model="registerData.confirmPassword" 
                      type="password" 
                      class="form-control"
                      placeholder="Повторите пароль"
                    >
                  </div>
                  <button 
                    @click="register" 
                    class="btn btn-success w-100"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
                  </button>
                </div>
                
                <!-- Сообщения об ошибках и успехе -->
                <div v-if="error" class="alert alert-danger mt-3">
                  {{ error }}
                </div>
                <div v-if="successMessage" class="alert alert-success mt-3">
                  {{ successMessage }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Дашборд -->
      <div v-else>
        <div class="row">
          <!-- Боковая панель с фильтрами и формами -->
          <div class="col-lg-3 mb-4">
            <!-- Форма добавления задачи -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">➕ Новая задача</h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <input 
                    v-model="newTask.title" 
                    type="text" 
                    class="form-control"
                    placeholder="Название задачи"
                  >
                </div>
                <div class="mb-3">
                  <textarea 
                    v-model="newTask.description" 
                    class="form-control" 
                    rows="2"
                    placeholder="Описание"
                  ></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Категория</label>
                  <select v-model="newTask.category_id" class="form-select">
                    <option :value="null">Без категории</option>
                    <option 
                      v-for="category in categories" 
                      :key="category.id" 
                      :value="category.id"
                      :style="`color: ${category.color}`"
                    >
                      {{ category.name }}
                    </option>
                  </select>
                </div>
                <div class="row mb-3">
                  <div class="col-6">
                    <label class="form-label">Приоритет</label>
                    <select v-model="newTask.priority" class="form-select">
                      <option value="1">🔵 Низкий</option>
                      <option value="2">🟢 Средний</option>
                      <option value="3">🟡 Высокий</option>
                      <option value="4">🟠 Срочный</option>
                      <option value="5">🔴 Критичный</option>
                    </select>
                  </div>
                  <div class="col-6">
                    <label class="form-label">Статус</label>
                    <select v-model="newTask.is_completed" class="form-select">
                      <option :value="false">Активная</option>
                      <option :value="true">Выполнена</option>
                    </select>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Дедлайн</label>
                  <input 
                    v-model="newTask.deadline" 
                    type="datetime-local" 
                    class="form-control"
                  >
                </div>
                <div class="mb-3">
                  <label class="form-label">Напоминание</label>
                  <input 
                    v-model="newTask.reminder" 
                    type="datetime-local" 
                    class="form-control"
                  >
                </div>
                <button 
                  @click="addTask" 
                  class="btn btn-primary w-100"
                  :disabled="!newTask.title || taskLoading"
                >
                  <span v-if="taskLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ taskLoading ? 'Добавление...' : 'Добавить задачу' }}
                </button>
              </div>
            </div>

            <!-- Форма добавления категории -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">📁 Новая категория</h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <input 
                    v-model="newCategory.name" 
                    type="text" 
                    class="form-control"
                    placeholder="Название категории"
                  >
                </div>
                <div class="mb-3">
                  <label class="form-label">Цвет</label>
                  <div class="d-flex gap-2">
                    <button 
                      v-for="color in categoryColors" 
                      :key="color"
                      class="btn color-btn"
                      :style="`background-color: ${color}; width: 30px; height: 30px; border: ${newCategory.color === color ? '3px solid #000' : '1px solid #dee2e6'}`"
                      @click="newCategory.color = color"
                    ></button>
                  </div>
                </div>
                <button 
                  @click="addCategory" 
                  class="btn btn-success w-100"
                  :disabled="!newCategory.name"
                >
                  Добавить категорию
                </button>
              </div>
            </div>

            <!-- Фильтры -->
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">🔍 Фильтры</h5>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label">Поиск</label>
                  <input 
                    v-model="filters.search" 
                    type="text" 
                    class="form-control"
                    placeholder="Поиск задач..."
                    @input="applyFilters"
                  >
                </div>
                <div class="mb-3">
                  <label class="form-label">Категория</label>
                  <select v-model="filters.category_id" class="form-select" @change="applyFilters">
                    <option :value="null">Все категории</option>
                    <option 
                      v-for="category in categories" 
                      :key="category.id" 
                      :value="category.id"
                    >
                      {{ category.name }} ({{ category.task_count }})
                    </option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">Приоритет</label>
                  <select v-model="filters.priority" class="form-select" @change="applyFilters">
                    <option :value="null">Все приоритеты</option>
                    <option value="1">🔵 Низкий</option>
                    <option value="2">🟢 Средний</option>
                    <option value="3">🟡 Высокий</option>
                    <option value="4">🟠 Срочный</option>
                    <option value="5">🔴 Критичный</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label class="form-label">Статус</label>
                  <select v-model="filters.completed" class="form-select" @change="applyFilters">
                    <option :value="null">Все задачи</option>
                    <option value="false">Активные</option>
                    <option value="true">Выполненные</option>
                  </select>
                </div>
                <button 
                  @click="resetFilters" 
                  class="btn btn-outline-secondary w-100"
                >
                  Сбросить фильтры
                </button>
              </div>
            </div>
          </div>

          <!-- Основной контент -->
          <div class="col-lg-9">
            <!-- Статистика -->
            <div class="row mb-4">
              <div class="col-md-3">
                <div class="card bg-primary text-white">
                  <div class="card-body text-center">
                    <h4>{{ totalTasksCount }}</h4>
                    <small>Всего задач</small>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-success text-white">
                  <div class="card-body text-center">
                    <h4>{{ completedTasksCount }}</h4>
                    <small>Выполнено</small>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-warning text-dark">
                  <div class="card-body text-center">
                    <h4>{{ activeTasksCount }}</h4>
                    <small>Активных</small>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-danger text-white">
                  <div class="card-body text-center">
                    <h4>{{ highPriorityTasksCount }}</h4>
                    <small>Высокий приоритет</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Заголовок и управление -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h2 class="mb-0">
                Мои задачи 
                <span class="badge bg-secondary">{{ filteredTasks?.length || 0 }}</span>
              </h2>
              <div>
                <button @click="loadTasks" class="btn btn-outline-primary btn-sm me-2" :disabled="taskLoading">
                  <span v-if="taskLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Обновить
                </button>
                <button @click="exportTasks" class="btn btn-outline-success btn-sm">
                  📊 Экспорт
                </button>
              </div>
            </div>

            <!-- Состояние загрузки -->
            <div v-if="taskLoading && (!filteredTasks || filteredTasks.length === 0)" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
              <p class="mt-2 text-muted">Загружаем задачи...</p>
            </div>

            <!-- Нет задач -->
            <div v-else-if="!filteredTasks || filteredTasks.length === 0" class="text-center py-5 text-muted">
              <p>🎉 {{ filtersApplied ? 'Задачи не найдены' : 'Пока нет задач!' }}</p>
              <p>{{ filtersApplied ? 'Попробуйте изменить фильтры' : 'Создайте первую задачу' }}</p>
              <button v-if="filtersApplied" @click="resetFilters" class="btn btn-primary mt-2">
                Сбросить фильтры
              </button>
            </div>

            <!-- Список задач -->
            <div v-else>
              <div 
                v-for="task in filteredTasks" 
                :key="task.id"
                class="card mb-3 task-card"
                :class="`priority-${task.priority} ${task.is_completed ? 'border-success' : ''}`"
              >
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                      <!-- Заголовок и метки -->
                      <div class="d-flex align-items-center mb-2">
                        <h6 :class="{ 'completed': task.is_completed }" class="mb-0 me-2">
                          {{ task.title }}
                        </h6>
                        <span v-if="task.category_id" class="badge me-1" :style="`background-color: ${task.category_color}`">
                          {{ task.category_name }}
                        </span>
                        <span class="badge" :class="getPriorityClass(task.priority)">
                          Приоритет: {{ task.priority }}
                        </span>
                        <span v-if="task.is_completed" class="badge bg-success ms-1">
                          ✅ Выполнено
                        </span>
                      </div>
                      
                      <!-- Описание -->
                      <p v-if="task.description" class="text-muted small mb-2">
                        {{ task.description }}
                      </p>
                      
                      <!-- Даты -->
                      <div class="small text-muted">
                        <div v-if="task.deadline" class="mb-1">
                          📅 Дедлайн: {{ formatDateTime(task.deadline) }}
                          <span v-if="isOverdue(task.deadline)" class="badge bg-danger ms-1">
                            Просрочено
                          </span>
                        </div>
                        <div v-if="task.reminder">
                          ⏰ Напоминание: {{ formatDateTime(task.reminder) }}
                        </div>
                        <div>
                          📝 Создано: {{ formatDateTime(task.created_at) }}
                        </div>
                      </div>
                    </div>
                    
                    <!-- Кнопки управления -->
                    <div class="btn-group ms-3 flex-shrink-0">
                      <button 
                        @click="editTask(task)"
                        class="btn btn-sm btn-outline-primary"
                        title="Редактировать"
                      >
                        ✏️
                      </button>
                      <button 
                        @click="toggleTask(task)"
                        class="btn btn-sm"
                        :class="task.is_completed ? 'btn-warning' : 'btn-success'"
                        :title="task.is_completed ? 'Вернуть в работу' : 'Отметить выполненной'"
                      >
                        {{ task.is_completed ? '↶' : '✓' }}
                      </button>
                      <button 
                        @click="deleteTask(task.id)"
                        class="btn btn-sm btn-danger"
                        title="Удалить задачу"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Модальное окно редактирования задачи -->
    <div v-if="editingTask" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактирование задачи</h5>
            <button type="button" class="btn-close" @click="editingTask = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название</label>
              <input v-model="editingTask.title" type="text" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">Описание</label>
              <textarea v-model="editingTask.description" class="form-control" rows="3"></textarea>
            </div>
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Категория</label>
                <select v-model="editingTask.category_id" class="form-select">
                  <option :value="null">Без категории</option>
                  <option 
                    v-for="category in categories" 
                    :key="category.id" 
                    :value="category.id"
                  >
                    {{ category.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Приоритет</label>
                <select v-model="editingTask.priority" class="form-select">
                  <option value="1">🔵 Низкий</option>
                  <option value="2">🟢 Средний</option>
                  <option value="3">🟡 Высокий</option>
                  <option value="4">🟠 Срочный</option>
                  <option value="5">🔴 Критичный</option>
                </select>
              </div>
            </div>
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Дедлайн</label>
                <input v-model="editingTask.deadline" type="datetime-local" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label">Напоминание</label>
                <input v-model="editingTask.reminder" type="datetime-local" class="form-control">
              </div>
            </div>
            <div class="form-check mb-3">
              <input v-model="editingTask.is_completed" type="checkbox" class="form-check-input" id="completedCheck">
              <label class="form-check-label" for="completedCheck">
                Задача выполнена
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="editingTask = null">Отмена</button>
            <button type="button" class="btn btn-primary" @click="saveTask">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'

export default {
  name: 'App',
  setup() {
    // Состояние аутентификации
    const token = ref(localStorage.getItem('token'))
    const currentUser = ref('')
    const loading = ref(false)
    const error = ref('')
    const successMessage = ref('')
    const activeTab = ref('login')

    // Данные
    const tasks = ref([])
    const categories = ref([])
    const taskLoading = ref(false)
    const editingTask = ref(null)

    // Формы
    const loginData = reactive({
      username: '',
      password: ''
    })

    const registerData = reactive({
      username: '',
      password: '',
      confirmPassword: ''
    })

    const newTask = reactive({
      title: '',
      description: '',
      priority: 1,
      category_id: null,
      is_completed: false,
      deadline: '',
      reminder: ''
    })

    const newCategory = reactive({
      name: '',
      color: '#6c757d'
    })

    const filters = reactive({
      search: '',
      category_id: null,
      priority: null,
      completed: null
    })

    const categoryColors = [
      '#dc3545', '#198754', '#0dcaf0', '#ffc107', '#6f42c1',
      '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0d6efd'
    ]

    // Вычисляемые свойства
    const isAuthenticated = computed(() => !!token.value)
    
    const filteredTasks = computed(() => {
      if (!tasks.value || !Array.isArray(tasks.value)) return []
      
      return tasks.value.filter(task => {
        // Поиск
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase()
          if (!task.title.toLowerCase().includes(searchTerm) && 
              !task.description.toLowerCase().includes(searchTerm)) {
            return false
          }
        }
        
        // Категория
        if (filters.category_id && task.category_id !== filters.category_id) {
          return false
        }
        
        // Приоритет
        if (filters.priority && task.priority !== parseInt(filters.priority)) {
          return false
        }
        
        // Статус
        if (filters.completed !== null) {
          const completedFilter = filters.completed === 'true'
          if (task.is_completed !== completedFilter) {
            return false
          }
        }
        
        return true
      })
    })

    const totalTasksCount = computed(() => tasks.value?.length || 0)
    const completedTasksCount = computed(() => tasks.value?.filter(t => t.is_completed).length || 0)
    const activeTasksCount = computed(() => tasks.value?.filter(t => !t.is_completed).length || 0)
    const highPriorityTasksCount = computed(() => tasks.value?.filter(t => t.priority >= 4).length || 0)
    const filtersApplied = computed(() => {
      return filters.search || filters.category_id || filters.priority || filters.completed !== null
    })

    // API функции
    async function apiRequest(url, options = {}) {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      }

      const baseUrl = 'http://localhost:5000/api'

      if (token.value) {
        config.headers.Authorization = `Bearer ${token.value}`
      }

      if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body)
      }

      // Добавляем параметры запроса для GET
      if (options.params && config.method === 'GET') {
        const params = new URLSearchParams()
        Object.keys(options.params).forEach(key => {
          if (options.params[key] !== null && options.params[key] !== undefined) {
            params.append(key, options.params[key])
          }
        })
        url += '?' + params.toString()
      }

      try {
        const response = await fetch(`${baseUrl}${url}`, config)
        
        if (response.status === 401) {
          logout()
          throw new Error('Сессия истекла. Войдите снова.')
        }
        
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.error || `Ошибка ${response.status}`)
        }
        
        return data
      } catch (err) {
        console.error('API Error:', err)
        throw err
      }
    }

    // Аутентификация
    async function login() {
      loading.value = true
      error.value = ''
      successMessage.value = ''
      
      try {
        if (!loginData.username || !loginData.password) {
          throw new Error('Заполните все поля')
        }
        
        const result = await apiRequest('/login', {
          method: 'POST',
          body: {
            username: loginData.username,
            password: loginData.password
          }
        })
        
        token.value = result.token
        currentUser.value = result.username
        localStorage.setItem('token', result.token)
        
        await loadInitialData()
        successMessage.value = 'Успешный вход!'
        
        // Очищаем форму после успешного входа
        Object.assign(loginData, {
          username: '',
          password: ''
        })
        
      } catch (err) {
        console.error('Login error:', err)
        error.value = err.message || 'Ошибка входа'
      } finally {
        loading.value = false
      }
    }

    async function register() {
      loading.value = true
      error.value = ''
      successMessage.value = ''
      
      if (!registerData.username || !registerData.password || !registerData.confirmPassword) {
        error.value = 'Заполните все поля'
        loading.value = false
        return
      }
      
      if (registerData.password !== registerData.confirmPassword) {
        error.value = 'Пароли не совпадают'
        loading.value = false
        return
      }
      
      if (registerData.password.length < 6) {
        error.value = 'Пароль должен быть не менее 6 символов'
        loading.value = false
        return
      }
      
      try {
        const result = await apiRequest('/register', {
          method: 'POST',
          body: {
            username: registerData.username,
            password: registerData.password
          }
        })
        
        token.value = result.token
        currentUser.value = result.username
        localStorage.setItem('token', result.token)
        
        await loadInitialData()
        successMessage.value = 'Регистрация успешна!'
        
        // Очищаем форму
        Object.assign(registerData, {
          username: '',
          password: '',
          confirmPassword: ''
        })
        
      } catch (err) {
        console.error('Registration error:', err)
        error.value = err.message || 'Ошибка регистрации'
      } finally {
        loading.value = false
      }
    }

    function logout() {
      token.value = null
      currentUser.value = ''
      localStorage.removeItem('token')
      tasks.value = []
      categories.value = []
      
      // Сбрасываем формы
      Object.assign(loginData, {
        username: '',
        password: ''
      })
      Object.assign(registerData, {
        username: '',
        password: '',
        confirmPassword: ''
      })
      
      activeTab.value = 'login'
      error.value = ''
      successMessage.value = ''
    }

    // Загрузка данных
    async function loadInitialData() {
      try {
        await Promise.all([loadTasks(), loadCategories()])
      } catch (err) {
        console.error('Error loading initial data:', err)
        error.value = 'Ошибка загрузки данных: ' + err.message
      }
    }

    async function loadTasks() {
      taskLoading.value = true
      try {
        const params = {}
        if (filters.category_id) params.category_id = filters.category_id
        if (filters.priority) params.priority = filters.priority
        if (filters.completed !== null) params.completed = filters.completed
        if (filters.search) params.search = filters.search
        
        tasks.value = await apiRequest('/tasks', { params })
      } catch (err) {
        error.value = 'Ошибка загрузки задач: ' + err.message
      } finally {
        taskLoading.value = false
      }
    }

    async function loadCategories() {
      try {
        categories.value = await apiRequest('/categories')
      } catch (err) {
        error.value = 'Ошибка загрузки категорий: ' + err.message
      }
    }

    // Задачи
    async function addTask() {
      if (!newTask.title.trim()) return
      
      taskLoading.value = true
      try {
        const taskData = { ...newTask }
        // Конвертируем пустые строки в null для дат
        if (!taskData.deadline) taskData.deadline = null
        if (!taskData.reminder) taskData.reminder = null
        
        await apiRequest('/tasks', {
          method: 'POST',
          body: taskData
        })
        
        // Сброс формы
        Object.assign(newTask, {
          title: '',
          description: '',
          priority: 1,
          category_id: null,
          is_completed: false,
          deadline: '',
          reminder: ''
        })
        
        await loadTasks()
        successMessage.value = 'Задача успешно создана!'
      } catch (err) {
        error.value = 'Ошибка создания задачи: ' + err.message
      } finally {
        taskLoading.value = false
      }
    }

    async function editTask(task) {
      editingTask.value = { ...task }
      // Конвертируем даты для input[type=datetime-local]
      if (editingTask.value.deadline) {
        editingTask.value.deadline = editingTask.value.deadline.slice(0, 16)
      }
      if (editingTask.value.reminder) {
        editingTask.value.reminder = editingTask.value.reminder.slice(0, 16)
      }
    }

    async function saveTask() {
      try {
        const taskData = { ...editingTask.value }
        // Конвертируем пустые строки в null для дат
        if (!taskData.deadline) taskData.deadline = null
        if (!taskData.reminder) taskData.reminder = null
        
        await apiRequest(`/tasks/${taskData.id}`, {
          method: 'PUT',
          body: taskData
        })
        
        editingTask.value = null
        await loadTasks()
        successMessage.value = 'Задача успешно обновлена!'
      } catch (err) {
        error.value = 'Ошибка обновления задачи: ' + err.message
      }
    }

    async function toggleTask(task) {
      try {
        await apiRequest(`/tasks/${task.id}`, {
          method: 'PUT',
          body: {
            ...task,
            is_completed: !task.is_completed
          }
        })
        await loadTasks()
      } catch (err) {
        error.value = 'Ошибка обновления задачи: ' + err.message
      }
    }

    async function deleteTask(taskId) {
      if (!confirm('Удалить эту задачу?')) return

      try {
        await apiRequest(`/tasks/${taskId}`, {
          method: 'DELETE'
        })
        await loadTasks()
        successMessage.value = 'Задача успешно удалена!'
      } catch (err) {
        error.value = 'Ошибка удаления задачи: ' + err.message
      }
    }

    // Категории
    async function addCategory() {
      if (!newCategory.name.trim()) return

      try {
        await apiRequest('/categories', {
          method: 'POST',
          body: newCategory
        })
        
        newCategory.name = ''
        newCategory.color = '#6c757d'
        await loadCategories()
        successMessage.value = 'Категория успешно создана!'
      } catch (err) {
        error.value = 'Ошибка создания категории: ' + err.message
      }
    }

    // Фильтры
    function applyFilters() {
      loadTasks()
    }

    function resetFilters() {
      Object.assign(filters, {
        search: '',
        category_id: null,
        priority: null,
        completed: null
      })
      loadTasks()
    }

    // Экспорт
    function exportTasks() {
      const data = {
        exportDate: new Date().toISOString(),
        user: currentUser.value,
        tasks: filteredTasks.value || [],
        statistics: {
          total: totalTasksCount.value,
          completed: completedTasksCount.value,
          active: activeTasksCount.value,
          highPriority: highPriorityTasksCount.value
        }
      }
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `tasks-${currentUser.value}-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    }

    // Вспомогательные функции
    function getPriorityClass(priority) {
      const classes = {
        1: 'bg-primary',
        2: 'bg-success',
        3: 'bg-warning',
        4: 'bg-orange',
        5: 'bg-danger'
      }
      return classes[priority] || 'bg-secondary'
    }

    function formatDateTime(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU')
    }

    function isOverdue(dateString) {
      if (!dateString) return false
      return new Date(dateString) < new Date()
    }

    onMounted(() => {
      if (token.value) {
        loadInitialData()
      }
    })

    return {
      // Состояние
      isAuthenticated,
      currentUser,
      loading,
      error,
      successMessage,
      activeTab,
      tasks,
      filteredTasks,
      categories,
      taskLoading,
      editingTask,
      
      // Данные форм
      loginData,
      registerData,
      newTask,
      newCategory,
      filters,
      categoryColors,
      
      // Вычисляемые свойства
      totalTasksCount,
      completedTasksCount,
      activeTasksCount,
      highPriorityTasksCount,
      filtersApplied,
      
      // Методы
      login,
      register,
      logout,
      loadTasks,
      addTask,
      editTask,
      saveTask,
      toggleTask,
      deleteTask,
      addCategory,
      applyFilters,
      resetFilters,
      exportTasks,
      getPriorityClass,
      formatDateTime,
      isOverdue
    }
  }
}
</script>

<style>
.priority-1 { border-left: 4px solid #0d6efd; }
.priority-2 { border-left: 4px solid #198754; }
.priority-3 { border-left: 4px solid #ffc107; }
.priority-4 { border-left: 4px solid #fd7e14; }
.priority-5 { border-left: 4px solid #dc3545; }

.completed {
  text-decoration: line-through;
  opacity: 0.7;
}

.bg-orange {
  background-color: #fd7e14 !important;
}

.color-btn {
  border-radius: 50%;
  padding: 0;
  min-width: 30px;
  min-height: 30px;
}

.task-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.nav-link.active {
  background-color: white !important;
  border-color: white !important;
}

.nav-link:not(.active) {
  background-color: transparent !important;
  border-color: transparent !important;
}
</style>