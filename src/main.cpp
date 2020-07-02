#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <mapbox/geometry/box.hpp>
#include <mapbox/geometry/point.hpp>
#include <mapbox/geometry/wagyu/edge.hpp>
#include <mapbox/geometry/wagyu/point.hpp>
#include <mapbox/geometry/wagyu/ring.hpp>
#include <sstream>

namespace py = pybind11;

#define MODULE_NAME _wagyu
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define BOX_NAME "Box"
#define EDGE_NAME "Edge"
#define POINT_NAME "Point"
#define POINT_NODE_NAME "PointNode"
#define RING_NAME "Ring"

using coordinate_t = double;
using Box = mapbox::geometry::box<coordinate_t>;
using Edge = mapbox::geometry::wagyu::edge<coordinate_t>;
using Point = mapbox::geometry::point<coordinate_t>;
using PointNode = mapbox::geometry::wagyu::point<coordinate_t>;
using PointNodePtr = mapbox::geometry::wagyu::point_ptr<coordinate_t>;
using Ring = mapbox::geometry::wagyu::ring<coordinate_t>;
using RingPtr = mapbox::geometry::wagyu::ring_ptr<coordinate_t>;
using RingVector = mapbox::geometry::wagyu::ring_vector<coordinate_t>;

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

template <class Object>
std::string repr(const Object& object) {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<double>::digits10 + 2);
  stream << object;
  return stream.str();
}

template <class Object>
static void write_maybe(std::ostream& stream, Object* value) {
  if (value == nullptr)
    stream << py::none();
  else
    stream << *value;
}

template <class Object>
static bool maybe_equal(Object* left, Object* right) {
  return left == nullptr ? right == nullptr
                         : right != nullptr && *left == *right;
}

template <class Object>
static bool vectors_equal(std::vector<Object*> left,
                          std::vector<Object*> right) {
  if (left.size() != right.size()) return false;
  auto size = left.size();
  for (std::size_t index = 0; index < size; ++index)
    if (!maybe_equal(left[index], right[index])) return false;
  return true;
}

template <typename Object>
static void write_vector(std::ostream& stream,
                         const std::vector<Object*>& elements) {
  stream << "[";
  if (!elements.empty()) {
    write_maybe(stream, elements[0]);
    std::for_each(std::next(std::begin(elements)), std::end(elements),
                  [&stream](Object* value) {
                    stream << ", ";
                    write_maybe(stream, value);
                  });
  }
  stream << "]";
};

namespace mapbox {
namespace geometry {
static std::ostream& operator<<(std::ostream& stream, const Point& point) {
  return stream << C_STR(MODULE_NAME) "." POINT_NAME "(" << point.x << ", "
                << point.y << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Box& box) {
  return stream << C_STR(MODULE_NAME) "." BOX_NAME "(" << box.min << ", "
                << box.max << ")";
}

namespace wagyu {
static std::ostream& operator<<(std::ostream& stream, const PointNode& point) {
  return stream << C_STR(MODULE_NAME) "." POINT_NODE_NAME "(" << point.x << ", "
                << point.y << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Ring& ring) {
  stream << C_STR(MODULE_NAME) "." RING_NAME "(" << ring.ring_index << ", ";
  write_vector(stream, ring.children);
  stream << ", ";
  write_maybe(stream, ring.points);
  stream << ", ";
  write_maybe(stream, ring.bottom_point);
  stream << ", " << bool_repr(ring.corrected) << ")";
  return stream;
}

static std::ostream& operator<<(std::ostream& stream, const Edge& edge) {
  return stream << C_STR(MODULE_NAME) "." EDGE_NAME "(" << edge.bot << ", "
                << edge.top << ")";
}

static bool operator==(const Edge& left, const Edge& right) {
  return left.bot == right.bot && left.top == right.top;
}

static bool operator==(const Ring& left, const Ring& right) {
  return left.ring_index == right.ring_index &&
         vectors_equal(left.children, right.children) &&
         maybe_equal(left.points, right.points) &&
         maybe_equal(left.bottom_point, right.bottom_point) &&
         left.corrected == right.corrected;
}
}  // namespace wagyu
}  // namespace geometry
}  // namespace mapbox

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of mapbox/wagyu library.
    )pbdoc";

  py::class_<Point>(m, POINT_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::pickle(
          [](const Point& self) {  // __getstate__
            return py::make_tuple(self.x, self.y);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Point(tuple[0].cast<coordinate_t>(),
                         tuple[1].cast<coordinate_t>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Point>)
      .def_readonly("x", &Point::x)
      .def_readonly("y", &Point::y);

  py::class_<PointNode, std::unique_ptr<PointNode, py::nodelete>>(
      m, POINT_NODE_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::self == py::self)
      .def("__repr__", repr<PointNode>)
      .def_readonly("x", &PointNode::x)
      .def_readonly("y", &PointNode::y)
      .def_readonly("next", &PointNode::next)
      .def_readonly("prev", &PointNode::prev);

  py::class_<Box>(m, BOX_NAME)
      .def(py::init<Point, Point>(), py::arg("min"), py::arg("max"))
      .def(py::pickle(
          [](const Box& self) {  // __getstate__
            return py::make_tuple(self.min, self.max);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Box(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Box>)
      .def_readonly("min", &Box::min)
      .def_readonly("max", &Box::max);

  py::class_<Edge>(m, EDGE_NAME)
      .def(py::init<Point, Point>(), py::arg("start"), py::arg("end"))
      .def(py::pickle(
          [](const Edge& self) {  // __getstate__
            return py::make_tuple(self.bot, self.top);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Edge(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Edge>)
      .def_readonly("bottom", &Edge::bot)
      .def_readonly("top", &Edge::top)
      .def_readonly("dx", &Edge::dx);

  py::class_<Ring, std::unique_ptr<Ring, py::nodelete>>(m, RING_NAME)
      .def(py::init<std::size_t, RingPtr, const RingVector&, PointNodePtr,
                    PointNodePtr, bool>(),
           py::arg("index") = 0, py::arg("parent").none(true) = nullptr,
           py::arg("children") = RingVector{},
           py::arg("node").none(true) = nullptr,
           py::arg("bottom_node").none(true) = nullptr,
           py::arg("corrected") = false)
      .def(py::self == py::self)
      .def("__repr__", repr<Ring>)
      .def_readonly("index", &Ring::ring_index)
      .def_readonly("box", &Ring::bbox)
      .def_readonly("parent", &Ring::parent)
      .def_readonly("children", &Ring::children)
      .def_readonly("node", &Ring::points)
      .def_readonly("bottom_node", &Ring::bottom_point)
      .def_readonly("corrected", &Ring::corrected)
      .def_property_readonly("size", &Ring::size)
      .def_property_readonly("area", &Ring::area)
      .def_property_readonly("is_hole", &Ring::is_hole)
      .def("recalculate_stats", &Ring::recalculate_stats)
      .def("reset_stats", &Ring::reset_stats)
      .def("set_stats", &Ring::set_stats, py::arg("area"), py::arg("size"),
           py::arg("box"));

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
