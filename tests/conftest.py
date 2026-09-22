"""Shared test fixtures and configuration."""
import pytest


@pytest.fixture
def simple_html():
    """Basic HTML with button and input."""
    return """
    <button>Login</button>
    <input type="email" placeholder="Email">
    """


@pytest.fixture
def form_html():
    """Complex form with various elements."""
    return """
    <form id="loginForm" class="auth-form">
        <h1>Sign In</h1>

        <label for="email">Email Address</label>
        <input id="email" type="email" required>

        <label for="password">Password</label>
        <input id="password" type="password" required>

        <input type="checkbox" id="remember" aria-label="Remember me">
        <label for="remember">Remember me</label>

        <button type="submit">Sign In</button>
        <button type="reset" aria-label="Clear form">Clear</button>

        <a href="/forgot-password">Forgot password?</a>
    </form>

    <div class="error-message" role="alert"></div>
    """


@pytest.fixture
def empty_html():
    """Empty HTML with no interactive elements."""
    return """
    <!-- just comments -->
    <p>Some text</p>
    """


@pytest.fixture
def malformed_html():
    """Malformed HTML with unclosed tags."""
    return """
    <button>Login
    <input type="email">
    <div>Not closed
    <p>Text</p>
    """


@pytest.fixture
def html_with_hidden_elements():
    """HTML with hidden and disabled elements."""
    return """
    <button>Visible</button>
    <button style="display: none;">Hidden</button>
    <button hidden>Also Hidden</button>
    <input disabled>
    <input type="text" disabled>
    """


@pytest.fixture
def html_with_duplicates():
    """HTML with duplicate IDs and elements."""
    return """
    <button id="btn">Button 1</button>
    <button id="btn">Button 2</button>
    <button></button>
    <button></button>
    """


@pytest.fixture
def html_with_special_chars():
    """HTML with special characters in labels and text."""
    return """
    <button>Sign-Up & Continue</button>
    <input placeholder="Email (required)">
    <label>Username/Email</label>
    <p>Cost: $99.99</p>
    """


@pytest.fixture
def html_with_aria():
    """HTML with ARIA attributes."""
    return """
    <div aria-label="Close dialog">✕</div>
    <button aria-label="Save changes">💾</button>
    <input aria-label="Search products">
    <div role="alert">Error message</div>
    <div role="status">Loading...</div>
    """


@pytest.fixture
def html_with_tables():
    """HTML with table structure."""
    return """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John</td>
                <td>john@example.com</td>
            </tr>
        </tbody>
    </table>
    """


@pytest.fixture
def html_with_script_style():
    """HTML with script and style tags that should be ignored."""
    return """
    <div>
        <button>Click me</button>
        <script>
            console.log("This should be ignored");
        </script>
        <style>
            button { color: red; }
        </style>
        <input type="email">
    </div>
    """


@pytest.fixture
def html_various_input_types():
    """HTML with various input types."""
    return """
    <input type="text" placeholder="Text">
    <input type="email" placeholder="Email">
    <input type="password" placeholder="Password">
    <input type="checkbox">
    <input type="radio">
    <input type="date">
    <input type="number">
    <textarea placeholder="Message"></textarea>
    <select><option>Choose</option></select>
    """


@pytest.fixture
def html_headings():
    """HTML with all heading levels."""
    return """
    <h1>Main Title</h1>
    <h2>Section</h2>
    <h3>Subsection</h3>
    <h4>Sub-subsection</h4>
    <h5>Small</h5>
    <h6>Smallest</h6>
    """


@pytest.fixture
def html_links():
    """HTML with various links."""
    return """
    <a href="/home">Home</a>
    <a href="/profile">Profile</a>
    <a href="https://example.com">External</a>
    """


@pytest.fixture
def html_lists():
    """HTML with list structures."""
    return """
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    <ol>
        <li>First</li>
        <li>Second</li>
    </ol>
    """


@pytest.fixture
def html_semantic_sections():
    """HTML with semantic section elements."""
    return """
    <header>
        <nav>Navigation</nav>
    </header>
    <main>
        <article>Article content</article>
        <section>Section content</section>
    </main>
    <footer>Footer</footer>
    """
