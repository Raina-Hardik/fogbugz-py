# fogbugz-py Development Roadmap

This document outlines the development plan for fogbugz-py from initial alpha through stable releases.

---

## Current Status: **Alpha** 🎯

Phase 3 (Core Client) now complete. Phase 4 (Polish) and Phase 5 (CLI) planned next.

---

## Version 0.1.0 - Alpha Release (Q1 2026)

**Goal**: Core async client with read-only operations

### Phase 1: Foundation ✅ COMPLETED
- [x] Project structure and scaffolding
- [x] Documentation (README, architecture docs)
- [x] Build system configuration (Hatch)
- [x] Test framework setup
- [x] PEP 561 compliance

### Phase 2: Core Infrastructure ✅ COMPLETED
- [x] HTTP transport layer (httpx.AsyncClient)
  - [x] Request/response handling
  - [x] Error mapping (4xx, 5xx → exceptions)
  - [x] Connection pooling
  - [x] Timeout management
- [x] Retry logic (Tenacity)
  - [x] Exponential backoff with jitter
  - [x] Configurable retry policies
  - [x] Conditional retries (5xx only)
- [x] Authentication
  - [x] API token support
  - [x] Username/password support (with warning)
  - [x] Auth header/param injection
- [x] Configuration system
  - [x] TOML file parsing
  - [x] Config file discovery
  - [x] Environment variable support
  - [x] Priority resolution (CLI > config > env)

### Phase 3: Core Client & Resources ✅ COMPLETED
- [x] Main FogBugzClient orchestrating class
  - [x] Async context manager support (`async with FogBugzClient() as client:`)
  - [x] Resource-oriented interface
  - [x] Proper lifecycle management
- [x] Cases resource
  - [x] `search()` implementation
  - [x] `get()` implementation
  - [x] Pydantic models with field aliasing
  - [x] Full test coverage (3 tests)
- [x] Projects resource
  - [x] `list()` implementation
  - [x] `get()` implementation
  - [x] Pydantic models with field aliasing
  - [x] Full test coverage (2 tests)
- [x] People resource
  - [x] `search()` implementation
  - [x] `get()` implementation
  - [x] Pydantic models with field aliasing
  - [x] Full test coverage (2 tests)

### Phase 4: Testing & Polish 🔄 IN PROGRESS
- [ ] Unit tests (>80% coverage)
  - [x] 83 tests currently passing
  - [ ] Additional edge case coverage
- [ ] Integration tests with respx mocking
  - [x] All transport tests passing
  - [ ] Additional resource integration tests
- [ ] Smoke tests passing
  - [x] 7 smoke tests passing
- [ ] Error handling tests
  - [x] Comprehensive error handling tests
- [ ] Documentation improvements
  - [ ] API usage examples
  - [ ] Advanced configuration guide
  - [ ] Troubleshooting guide
- [ ] Type checking (mypy) passing
- [ ] Linting (ruff) passing

### Phase 5: Optional Features
- [x] CLI (typer extra)
  - [x] `fogbugz search` command
  - [x] `fogbugz case get` command
  - [x] `fogbugz case events` command
  - [x] `fogbugz projects list` command
  - [x] `fogbugz projects get` command
  - [x] `fogbugz people search` command
  - [x] `fogbugz people get` command
  - [x] `fogbugz whoami` command
  - [x] Rich table output
- [ ] Structured logging (logging extra)
  - [ ] structlog configuration
  - [ ] Request/response logging
  - [ ] Retry logging

**Release Criteria**:
- ✅ All Phase 2-4 tasks completed
- ✅ >80% test coverage
- ✅ All smoke tests passing
- ✅ Documentation complete with working examples
- ✅ Type hints validated
- ✅ CLI read commands working (if extra installed)

---

## Version 0.2.0 - Beta Release (Q2 2026)

**Goal**: Enhanced features and stability improvements

### Planned Features
- [ ] Pagination support for search results
- [ ] Rate limiting awareness
- [ ] Request/response caching (optional)
- [ ] Additional case fields
- [ ] Additional project fields
- [ ] Batch operations (parallel requests)
- [ ] Progress indicators for CLI
- [ ] JSON output for CLI
- [ ] Config file validation
- [ ] Better error messages
- [ ] Logging improvements

### Quality Improvements
- [ ] >90% test coverage
- [ ] Performance benchmarks
- [ ] Memory profiling
- [ ] Documentation site (MkDocs?)
- [ ] API reference documentation
- [ ] More usage examples
- [ ] Migration guide (if breaking changes)

**Release Criteria**:
- ✅ All planned features implemented
- ✅ >90% test coverage
- ✅ Performance benchmarks established
- ✅ No known critical bugs
- ✅ Beta testing feedback addressed

---

## Version 0.3.0 - Write Operations (Q3 2026)

**Goal**: Add write/mutate operations

### Write Support
- [ ] Case creation
  - [ ] `cases.create()` method
  - [ ] Input validation
  - [ ] Required fields
- [ ] Case updates
  - [ ] `cases.update()` method
  - [ ] Partial updates
  - [ ] Status changes
  - [ ] Assignment changes
- [ ] Case comments
  - [ ] `cases.add_comment()` method
  - [ ] Comment formatting
- [ ] Attachments (if feasible)
  - [ ] Upload support
  - [ ] Download support

### CLI Write Commands
- [ ] `fogbugz case create`
- [ ] `fogbugz case update`
- [ ] `fogbugz case comment`

### Safety Features
- [ ] Confirmation prompts for destructive operations
- [ ] Dry-run mode
- [ ] Validation before submission
- [ ] Rollback support (where possible)

**Release Criteria**:
- ✅ Core write operations working
- ✅ Safety features implemented
- ✅ Tests for all write operations
- ✅ Documentation updated
- ✅ CLI commands functional

---

## Version 1.0.0 - Stable Release (Q4 2026)

**Goal**: Production-ready, stable API

### Stability Focus
- [ ] API freeze (no breaking changes)
- [ ] Comprehensive documentation
- [ ] Full test coverage (>95%)
- [ ] Performance optimizations
- [ ] Security audit
- [ ] Dependency updates
- [ ] Error message improvements
- [ ] Logging standardization

### Documentation
- [ ] Complete API reference
- [ ] User guide
- [ ] Best practices guide
- [ ] Migration guides
- [ ] Troubleshooting guide
- [ ] Contributing guide
- [ ] Security policy
- [ ] Code of conduct

### Quality Assurance
- [ ] Load testing
- [ ] Edge case testing
- [ ] Error recovery testing
- [ ] Timeout testing
- [ ] Network failure testing
- [ ] Authentication failure testing

**Release Criteria**:
- ✅ Stable API (semver compliance)
- ✅ >95% test coverage
- ✅ All documentation complete
- ✅ No known critical or high-priority bugs
- ✅ Performance benchmarks met
- ✅ Security audit passed
- ✅ Community feedback incorporated

---

## Post-1.0 Roadmap

### Version 1.1+ - Advanced Features
- [ ] Custom fields support
- [ ] Advanced search filters
- [ ] Search query builder
- [ ] Webhooks (if FogBugz supports)
- [ ] Real-time updates (if feasible)
- [ ] Export functionality
- [ ] Bulk operations optimization
- [ ] GraphQL support (if FogBugz adds it)

### Version 2.0+ - Major Enhancements
- [ ] Plugin system
- [ ] Custom resources
- [ ] Advanced caching strategies
- [ ] Offline mode
- [ ] Sync API wrapper (if demand exists)
- [ ] Multi-instance support
- [ ] Advanced CLI features (interactive mode?)

---

## Slim Variant Strategy

The `fogbugz-py-slim` variant (no pydantic) will be maintained in parallel:

- **v0.1.0**: Conditional imports, dict responses
- **v0.2.0+**: Feature parity with dict-based responses
- **Evaluation at v1.0**: Assess if separate distribution is needed

---

## Community & Ecosystem

### Short-term
- [ ] GitHub repository setup
- [ ] Issue templates
- [ ] Pull request templates
- [ ] Contribution guidelines
- [ ] Code of conduct

### Medium-term
- [ ] Discord/Slack community?
- [ ] Plugin ecosystem
- [ ] Example projects
- [ ] Integration examples (CI/CD, etc.)
- [ ] Blog posts / tutorials

### Long-term
- [ ] Conference talks
- [ ] Workshop materials
- [ ] Certification program?
- [ ] Enterprise support options

---

## Technical Debt & Maintenance

### Ongoing
- Dependency updates (monthly)
- Security patches (as needed)
- Bug fixes (as reported)
- Performance monitoring
- Test suite maintenance

### Quarterly Reviews
- Architecture review
- Code quality metrics
- Test coverage analysis
- Performance benchmarks
- User feedback review
- Dependency audit

---

## Success Metrics

### Version 0.1.0
- [ ] 50+ GitHub stars
- [ ] 5+ contributors
- [ ] 100+ PyPI downloads/month

### Version 1.0.0
- [ ] 200+ GitHub stars
- [ ] 20+ contributors
- [ ] 1000+ PyPI downloads/month
- [ ] 5+ companies using in production

---

## Breaking Changes Policy

Starting from v1.0.0:
- **Major version** (2.0, 3.0): Breaking changes allowed
- **Minor version** (1.1, 1.2): New features, no breaking changes
- **Patch version** (1.0.1): Bug fixes only

Pre-1.0 releases may include breaking changes in minor versions with clear migration guides.

---

## Open Questions

1. **Slim vs Full**: Should we maintain separate PyPI packages or just extras?
2. **Sync API**: Is there demand for a synchronous wrapper?
3. **CLI Scope**: How far should CLI features go?
4. **Write Operations**: Which write operations are most valuable?
5. **Custom Fields**: How to handle FogBugz custom fields generically?

---

## Contributing to Roadmap

This roadmap is not set in stone. Community feedback is welcome:

- Open an issue with label `roadmap`
- Start a discussion in GitHub Discussions
- Submit a PR with roadmap updates
- Vote on features using GitHub reactions

---

## Changelog

- **2026-01-09**: Initial roadmap created
- **TBD**: Next update after v0.1.0 release

---

**Last Updated**: January 9, 2026  
**Current Version**: Pre-Alpha (v0.1.0-dev)  
**Next Milestone**: v0.1.0 Alpha Release
